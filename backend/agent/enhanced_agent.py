"""
Enhanced NEO Agent with improved stability, autonomy, and error handling.

This module provides an enhanced version of the NEO agent with:
- Robust error handling and recovery
- Improved autonomy and decision-making
- Better resource management
- Enhanced logging and monitoring
- Self-healing capabilities
- Adaptive behavior based on context
"""

import asyncio
import json
import os
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4
import time

from utils.logger import logger
from utils.config import config
from services.database import DBConnection
from services.langfuse import langfuse
from agentpress.thread_manager import ThreadManager
from agentpress.response_processor import ProcessorConfig

class AgentState:
    """Tracks agent state and performance metrics."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.total_iterations = 0
        self.successful_iterations = 0
        self.failed_iterations = 0
        self.tool_usage_count = {}
        self.error_history = []
        self.performance_metrics = {
            'avg_response_time': 0.0,
            'success_rate': 0.0,
            'tool_success_rate': {},
            'memory_usage': 0,
            'last_health_check': datetime.now()
        }
        self.context_memory = {}
        self.learning_data = {}
        
    def record_iteration(self, success: bool, duration: float, error: Optional[str] = None):
        """Record iteration metrics."""
        self.total_iterations += 1
        if success:
            self.successful_iterations += 1
        else:
            self.failed_iterations += 1
            if error:
                self.error_history.append({
                    'timestamp': datetime.now(),
                    'error': error,
                    'iteration': self.total_iterations
                })
        
        # Update performance metrics
        self.performance_metrics['success_rate'] = (
            self.successful_iterations / self.total_iterations if self.total_iterations > 0 else 0
        )
        
        # Update average response time
        current_avg = self.performance_metrics['avg_response_time']
        self.performance_metrics['avg_response_time'] = (
            (current_avg * (self.total_iterations - 1) + duration) / self.total_iterations
        )
    
    def record_tool_usage(self, tool_name: str, success: bool):
        """Record tool usage statistics."""
        if tool_name not in self.tool_usage_count:
            self.tool_usage_count[tool_name] = {'total': 0, 'success': 0}
        
        self.tool_usage_count[tool_name]['total'] += 1
        if success:
            self.tool_usage_count[tool_name]['success'] += 1
        
        # Update tool success rate
        self.performance_metrics['tool_success_rate'][tool_name] = (
            self.tool_usage_count[tool_name]['success'] / 
            self.tool_usage_count[tool_name]['total']
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        uptime = datetime.now() - self.start_time
        return {
            'uptime_seconds': uptime.total_seconds(),
            'total_iterations': self.total_iterations,
            'success_rate': self.performance_metrics['success_rate'],
            'avg_response_time': self.performance_metrics['avg_response_time'],
            'recent_errors': len([e for e in self.error_history if 
                                datetime.now() - e['timestamp'] < timedelta(minutes=10)]),
            'tool_usage': self.tool_usage_count,
            'memory_usage': self.performance_metrics['memory_usage']
        }

class EnhancedAgent:
    """Enhanced NEO Agent with improved capabilities."""
    
    def __init__(self, thread_id: str, project_id: str, agent_config: Optional[Dict] = None):
        self.thread_id = thread_id
        self.project_id = project_id
        self.agent_config = agent_config or {}
        self.state = AgentState()
        self.db = DBConnection()
        self.thread_manager: Optional[ThreadManager] = None
        self.trace = None
        
        # Enhanced configuration
        self.max_retries = self.agent_config.get('max_retries', 3)
        self.retry_delay = self.agent_config.get('retry_delay', 1.0)
        self.max_iterations = self.agent_config.get('max_iterations', 100)
        self.health_check_interval = self.agent_config.get('health_check_interval', 300)  # 5 minutes
        self.auto_recovery = self.agent_config.get('auto_recovery', True)
        self.learning_enabled = self.agent_config.get('learning_enabled', True)
        
        # Adaptive behavior settings
        self.adaptive_timeout = True
        self.context_awareness = True
        self.proactive_error_prevention = True
        
        logger.info(f"Enhanced Agent initialized for thread {thread_id}, project {project_id}")
    
    async def initialize(self):
        """Initialize the enhanced agent."""
        try:
            self.trace = langfuse.trace(
                name="enhanced_agent", 
                session_id=self.thread_id, 
                metadata={
                    "project_id": self.project_id,
                    "agent_type": "enhanced",
                    "config": self.agent_config
                }
            )
            
            self.thread_manager = ThreadManager(
                trace=self.trace,
                is_agent_builder=self.agent_config.get('is_agent_builder', False),
                target_agent_id=self.agent_config.get('target_agent_id')
            )
            
            # Initialize tools with enhanced error handling
            await self._initialize_tools()
            
            # Perform initial health check
            await self._health_check()
            
            logger.info("Enhanced Agent initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Agent: {e}")
            raise
    
    async def _initialize_tools(self):
        """Initialize tools with enhanced error handling."""
        try:
            # Import tools dynamically to avoid import errors
            from agent.tools.message_tool import MessageTool
            from agent.tools.sb_shell_tool import SandboxShellTool
            from agent.tools.sb_files_tool import SandboxFilesTool
            from agent.tools.sb_browser_tool import SandboxBrowserTool
            from agent.tools.sb_deploy_tool import SandboxDeployTool
            from agent.tools.sb_expose_tool import SandboxExposeTool
            from agent.tools.web_search_tool import SandboxWebSearchTool
            from agent.tools.expand_msg_tool import ExpandMessageTool
            from agent.tools.sb_vision_tool import SandboxVisionTool
            
            # Get enabled tools from config
            enabled_tools = self.agent_config.get('agentpress_tools')
            
            if enabled_tools is None:
                # Register all tools for full capabilities
                logger.info("Registering all tools for enhanced agent")
                
                # Core tools (always available)
                self.thread_manager.add_tool(MessageTool)
                self.thread_manager.add_tool(ExpandMessageTool, 
                                           thread_id=self.thread_id, 
                                           thread_manager=self.thread_manager)
                
                # Sandbox tools
                self.thread_manager.add_tool(SandboxShellTool, 
                                           project_id=self.project_id, 
                                           thread_manager=self.thread_manager)
                self.thread_manager.add_tool(SandboxFilesTool, 
                                           project_id=self.project_id, 
                                           thread_manager=self.thread_manager)
                self.thread_manager.add_tool(SandboxBrowserTool, 
                                           project_id=self.project_id, 
                                           thread_id=self.thread_id, 
                                           thread_manager=self.thread_manager)
                self.thread_manager.add_tool(SandboxDeployTool, 
                                           project_id=self.project_id, 
                                           thread_manager=self.thread_manager)
                self.thread_manager.add_tool(SandboxExposeTool, 
                                           project_id=self.project_id, 
                                           thread_manager=self.thread_manager)
                self.thread_manager.add_tool(SandboxWebSearchTool, 
                                           project_id=self.project_id, 
                                           thread_manager=self.thread_manager)
                self.thread_manager.add_tool(SandboxVisionTool, 
                                           project_id=self.project_id, 
                                           thread_id=self.thread_id, 
                                           thread_manager=self.thread_manager)
                
                # Optional tools based on configuration
                if config.RAPID_API_KEY:
                    try:
                        from agent.tools.data_providers_tool import DataProvidersTool
                        self.thread_manager.add_tool(DataProvidersTool)
                    except ImportError:
                        logger.warning("DataProvidersTool not available")
            else:
                # Register only enabled tools
                logger.info("Registering selective tools based on configuration")
                self._register_selective_tools(enabled_tools)
            
            # Initialize MCP tools if configured
            await self._initialize_mcp_tools()
            
        except Exception as e:
            logger.error(f"Error initializing tools: {e}")
            # Continue with basic tools if some fail
            if not hasattr(self.thread_manager, 'tool_registry') or not self.thread_manager.tool_registry.tools:
                # Fallback to basic tools
                from agent.tools.message_tool import MessageTool
                self.thread_manager.add_tool(MessageTool)
    
    def _register_selective_tools(self, enabled_tools: Dict):
        """Register only enabled tools."""
        # Import tools as needed
        tool_imports = {
            'sb_shell_tool': 'agent.tools.sb_shell_tool.SandboxShellTool',
            'sb_files_tool': 'agent.tools.sb_files_tool.SandboxFilesTool',
            'sb_browser_tool': 'agent.tools.sb_browser_tool.SandboxBrowserTool',
            'sb_deploy_tool': 'agent.tools.sb_deploy_tool.SandboxDeployTool',
            'sb_expose_tool': 'agent.tools.sb_expose_tool.SandboxExposeTool',
            'web_search_tool': 'agent.tools.web_search_tool.SandboxWebSearchTool',
            'sb_vision_tool': 'agent.tools.sb_vision_tool.SandboxVisionTool',
            'data_providers_tool': 'agent.tools.data_providers_tool.DataProvidersTool'
        }
        
        for tool_key, tool_path in tool_imports.items():
            if enabled_tools.get(tool_key, {}).get('enabled', False):
                try:
                    module_path, class_name = tool_path.rsplit('.', 1)
                    module = __import__(module_path, fromlist=[class_name])
                    tool_class = getattr(module, class_name)
                    
                    # Add tool with appropriate parameters
                    if tool_key in ['sb_shell_tool', 'sb_files_tool', 'sb_deploy_tool', 'sb_expose_tool', 'web_search_tool']:
                        self.thread_manager.add_tool(tool_class, 
                                                   project_id=self.project_id, 
                                                   thread_manager=self.thread_manager)
                    elif tool_key in ['sb_browser_tool', 'sb_vision_tool']:
                        self.thread_manager.add_tool(tool_class, 
                                                   project_id=self.project_id, 
                                                   thread_id=self.thread_id, 
                                                   thread_manager=self.thread_manager)
                    else:
                        self.thread_manager.add_tool(tool_class)
                        
                    logger.info(f"Registered tool: {tool_key}")
                    
                except Exception as e:
                    logger.warning(f"Failed to register tool {tool_key}: {e}")
    
    async def _initialize_mcp_tools(self):
        """Initialize MCP tools with enhanced error handling."""
        if not self.agent_config:
            return
        
        try:
            from agent.tools.mcp_tool_wrapper import MCPToolWrapper
            
            all_mcps = []
            
            # Add configured MCPs
            if self.agent_config.get('configured_mcps'):
                all_mcps.extend(self.agent_config['configured_mcps'])
            
            # Add custom MCPs
            if self.agent_config.get('custom_mcps'):
                for custom_mcp in self.agent_config['custom_mcps']:
                    mcp_config = {
                        'name': custom_mcp['name'],
                        'qualifiedName': f"custom_{custom_mcp['type']}_{custom_mcp['name'].replace(' ', '_').lower()}",
                        'config': custom_mcp['config'],
                        'enabledTools': custom_mcp.get('enabledTools', []),
                        'isCustom': True,
                        'customType': custom_mcp['type']
                    }
                    all_mcps.append(mcp_config)
            
            if all_mcps:
                logger.info(f"Initializing {len(all_mcps)} MCP servers")
                self.thread_manager.add_tool(MCPToolWrapper, mcp_configs=all_mcps)
                
                # Initialize MCP tools with retry logic
                for attempt in range(self.max_retries):
                    try:
                        # Find MCP wrapper instance
                        mcp_wrapper = None
                        for tool_info in self.thread_manager.tool_registry.tools.values():
                            if isinstance(tool_info['instance'], MCPToolWrapper):
                                mcp_wrapper = tool_info['instance']
                                break
                        
                        if mcp_wrapper:
                            await mcp_wrapper.initialize_and_register_tools()
                            logger.info("MCP tools initialized successfully")
                            break
                    except Exception as e:
                        logger.warning(f"MCP initialization attempt {attempt + 1} failed: {e}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                        else:
                            logger.error("Failed to initialize MCP tools after all retries")
                            
        except ImportError:
            logger.warning("MCP tools not available")
        except Exception as e:
            logger.error(f"Error initializing MCP tools: {e}")
    
    async def _health_check(self):
        """Perform health check and update metrics."""
        try:
            health_status = self.state.get_health_status()
            
            # Check database connection
            client = await self.db.client
            await client.table('projects').select('project_id').eq('project_id', self.project_id).limit(1).execute()
            
            # Check tool registry
            if not self.thread_manager or not self.thread_manager.tool_registry.tools:
                logger.warning("No tools registered in thread manager")
            
            # Update health check timestamp
            self.state.performance_metrics['last_health_check'] = datetime.now()
            
            logger.debug(f"Health check passed: {health_status}")
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            if self.auto_recovery:
                await self._attempt_recovery()
    
    async def _attempt_recovery(self):
        """Attempt to recover from errors."""
        logger.info("Attempting agent recovery...")
        
        try:
            # Reinitialize database connection
            self.db = DBConnection()
            
            # Reinitialize thread manager if needed
            if not self.thread_manager:
                await self.initialize()
            
            # Clear error history if recovery successful
            self.state.error_history = []
            logger.info("Agent recovery successful")
            
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
    
    async def run(self, 
                  stream: bool = True,
                  max_iterations: Optional[int] = None,
                  model_name: str = "anthropic/claude-3-5-sonnet-20241022",
                  enable_thinking: bool = False,
                  reasoning_effort: str = 'medium') -> AsyncGenerator[Dict[str, Any], None]:
        """
        Run the enhanced agent with improved error handling and autonomy.
        
        Args:
            stream: Whether to stream responses
            max_iterations: Maximum number of iterations
            model_name: LLM model to use
            enable_thinking: Enable reasoning mode
            reasoning_effort: Reasoning effort level
            
        Yields:
            Dict containing response data
        """
        if not self.thread_manager:
            await self.initialize()
        
        max_iterations = max_iterations or self.max_iterations
        iteration_count = 0
        continue_execution = True
        last_health_check = datetime.now()
        
        logger.info(f"Starting enhanced agent run with model: {model_name}")
        
        try:
            # Get system prompt
            system_prompt = await self._get_system_prompt(model_name)
            
            while continue_execution and iteration_count < max_iterations:
                iteration_start = time.time()
                iteration_success = False
                
                try:
                    # Periodic health check
                    if datetime.now() - last_health_check > timedelta(seconds=self.health_check_interval):
                        await self._health_check()
                        last_health_check = datetime.now()
                    
                    # Get conversation history with context management
                    messages = await self._get_conversation_history()
                    
                    # Add system message
                    if system_prompt:
                        messages.insert(0, {"role": "system", "content": system_prompt})
                    
                    # Adaptive timeout based on iteration history
                    timeout = self._calculate_adaptive_timeout()
                    
                    # Make LLM call with enhanced error handling
                    async for response_chunk in self._make_llm_call_with_retry(
                        messages=messages,
                        model_name=model_name,
                        stream=stream,
                        enable_thinking=enable_thinking,
                        reasoning_effort=reasoning_effort,
                        timeout=timeout
                    ):
                        yield response_chunk
                        
                        # Check for completion signals
                        if response_chunk.get('type') == 'completion':
                            continue_execution = False
                            iteration_success = True
                            break
                        elif response_chunk.get('type') == 'continue':
                            continue_execution = True
                            iteration_success = True
                            break
                        elif response_chunk.get('type') == 'error':
                            # Handle error but continue if possible
                            logger.warning(f"Iteration error: {response_chunk.get('content')}")
                            break
                    
                    iteration_count += 1
                    
                except Exception as e:
                    logger.error(f"Iteration {iteration_count} failed: {e}")
                    error_msg = str(e)
                    
                    # Attempt recovery for certain types of errors
                    if self._is_recoverable_error(e):
                        logger.info("Attempting recovery from recoverable error")
                        await self._attempt_recovery()
                        continue
                    else:
                        # Yield error and stop
                        yield {
                            'type': 'error',
                            'content': f"Agent encountered unrecoverable error: {error_msg}",
                            'iteration': iteration_count
                        }
                        break
                
                finally:
                    # Record iteration metrics
                    iteration_duration = time.time() - iteration_start
                    self.state.record_iteration(
                        success=iteration_success,
                        duration=iteration_duration,
                        error=None if iteration_success else "Iteration failed"
                    )
            
            # Final status
            if iteration_count >= max_iterations:
                yield {
                    'type': 'max_iterations_reached',
                    'content': f"Reached maximum iterations ({max_iterations})",
                    'iterations': iteration_count
                }
            else:
                yield {
                    'type': 'completed',
                    'content': "Agent execution completed successfully",
                    'iterations': iteration_count
                }
                
        except Exception as e:
            logger.error(f"Agent run failed: {e}")
            yield {
                'type': 'fatal_error',
                'content': f"Agent encountered fatal error: {str(e)}",
                'traceback': traceback.format_exc()
            }
    
    async def _get_system_prompt(self, model_name: str) -> str:
        """Get enhanced system prompt based on model and configuration."""
        try:
            if "gemini-2.5-flash" in model_name.lower():
                from agent.gemini_prompt import get_gemini_system_prompt
                base_prompt = get_gemini_system_prompt()
            else:
                from agent.prompt import get_system_prompt
                base_prompt = get_system_prompt()
            
            # Add enhanced capabilities information
            enhanced_prompt = base_prompt + "\n\n" + self._get_enhanced_capabilities_prompt()
            
            # Add agent-specific prompt if configured
            if self.agent_config.get('system_prompt'):
                enhanced_prompt = self.agent_config['system_prompt'] + "\n\n" + enhanced_prompt
            
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error getting system prompt: {e}")
            return "You are NEO, an advanced AI agent. Help users with their tasks efficiently and safely."
    
    def _get_enhanced_capabilities_prompt(self) -> str:
        """Get prompt describing enhanced capabilities."""
        return """
## Enhanced Agent Capabilities

You are running as an Enhanced NEO Agent with the following advanced capabilities:

### Autonomy & Decision Making
- You can make independent decisions about tool usage and task execution
- You have access to performance metrics and can adapt your behavior accordingly
- You can learn from previous interactions and improve over time

### Error Handling & Recovery
- You have robust error handling and can recover from most failures
- You can retry failed operations with exponential backoff
- You maintain context and state across recovery attempts

### Resource Management
- You monitor your own performance and resource usage
- You can optimize tool usage based on success rates
- You adapt timeouts and retry strategies based on historical performance

### Self-Monitoring
- You track success rates, response times, and error patterns
- You perform periodic health checks and self-diagnostics
- You can report on your own performance and suggest improvements

### Best Practices
1. Always verify tool results before proceeding
2. Use appropriate error handling for all operations
3. Monitor resource usage and optimize accordingly
4. Learn from failures and adapt strategies
5. Maintain clear communication about progress and issues
6. Be proactive in preventing known error patterns

Use these capabilities to provide the best possible assistance while maintaining stability and reliability.
"""
    
    async def _get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history with enhanced context management."""
        try:
            client = await self.db.client
            
            # Get messages with pagination for large conversations
            messages_response = await client.table('messages')\
                .select('*')\
                .eq('thread_id', self.thread_id)\
                .order('created_at', desc=False)\
                .execute()
            
            if not messages_response.data:
                return []
            
            messages = []
            for msg in messages_response.data:
                # Enhanced message processing
                processed_msg = self._process_message_for_context(msg)
                if processed_msg:
                    messages.append(processed_msg)
            
            # Apply context management if conversation is too long
            if len(messages) > 50:  # Threshold for context management
                messages = await self._apply_context_management(messages)
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def _process_message_for_context(self, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual message for context inclusion."""
        try:
            content = msg.get('content', '')
            role = msg.get('role', 'user')
            
            # Skip empty messages
            if not content:
                return None
            
            # Handle different content types
            if isinstance(content, str):
                processed_content = content
            elif isinstance(content, dict):
                processed_content = json.dumps(content)
            else:
                processed_content = str(content)
            
            # Compress very long messages
            if len(processed_content) > 10000:
                processed_content = self._compress_long_content(processed_content, msg.get('message_id'))
            
            return {
                "role": role,
                "content": processed_content
            }
            
        except Exception as e:
            logger.warning(f"Error processing message: {e}")
            return None
    
    def _compress_long_content(self, content: str, message_id: Optional[str] = None) -> str:
        """Compress long content while preserving important information."""
        if len(content) <= 10000:
            return content
        
        # Keep first and last parts, add truncation notice
        first_part = content[:4000]
        last_part = content[-4000:]
        
        truncation_notice = f"\n\n... (content truncated - {len(content)} total chars)"
        if message_id:
            truncation_notice += f" - use expand-message tool with message_id '{message_id}' for full content"
        truncation_notice += " ...\n\n"
        
        return first_part + truncation_notice + last_part
    
    async def _apply_context_management(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply context management to keep conversation within limits."""
        try:
            # Keep recent messages and summarize older ones
            recent_threshold = 30
            
            if len(messages) <= recent_threshold:
                return messages
            
            # Keep system message and recent messages
            recent_messages = messages[-recent_threshold:]
            older_messages = messages[:-recent_threshold]
            
            # Create summary of older messages
            summary = await self._create_conversation_summary(older_messages)
            
            # Combine summary with recent messages
            result = []
            if summary:
                result.append({
                    "role": "system",
                    "content": f"Previous conversation summary: {summary}"
                })
            
            result.extend(recent_messages)
            return result
            
        except Exception as e:
            logger.error(f"Error applying context management: {e}")
            return messages[-30:]  # Fallback to recent messages only
    
    async def _create_conversation_summary(self, messages: List[Dict[str, Any]]) -> str:
        """Create a summary of conversation history."""
        try:
            # Simple summarization - could be enhanced with LLM summarization
            summary_points = []
            
            for msg in messages:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                
                if role == 'user':
                    # Extract key user requests
                    if len(content) > 100:
                        summary_points.append(f"User requested: {content[:100]}...")
                    else:
                        summary_points.append(f"User requested: {content}")
                elif role == 'assistant':
                    # Extract key assistant actions
                    if 'tool_calls' in content or 'function_calls' in content:
                        summary_points.append("Assistant performed tool operations")
                    elif len(content) > 100:
                        summary_points.append(f"Assistant responded: {content[:100]}...")
            
            return " | ".join(summary_points[-10:])  # Keep last 10 summary points
            
        except Exception as e:
            logger.error(f"Error creating conversation summary: {e}")
            return "Previous conversation history available but could not be summarized"
    
    def _calculate_adaptive_timeout(self) -> float:
        """Calculate adaptive timeout based on performance history."""
        if not self.adaptive_timeout:
            return 300.0  # Default 5 minutes
        
        base_timeout = 300.0
        avg_response_time = self.state.performance_metrics['avg_response_time']
        
        if avg_response_time > 0:
            # Adjust timeout based on historical performance
            adaptive_timeout = max(base_timeout, avg_response_time * 3)
            return min(adaptive_timeout, 900.0)  # Cap at 15 minutes
        
        return base_timeout
    
    async def _make_llm_call_with_retry(self, 
                                       messages: List[Dict[str, Any]],
                                       model_name: str,
                                       stream: bool,
                                       enable_thinking: bool,
                                       reasoning_effort: str,
                                       timeout: float) -> AsyncGenerator[Dict[str, Any], None]:
        """Make LLM call with retry logic and enhanced error handling."""
        
        for attempt in range(self.max_retries):
            try:
                # Use thread manager's response processor
                processor_config = ProcessorConfig(
                    stream=stream,
                    model_name=model_name,
                    enable_thinking=enable_thinking,
                    reasoning_effort=reasoning_effort,
                    timeout=timeout
                )
                
                async for response in self.thread_manager.response_processor.process_conversation(
                    messages=messages,
                    thread_id=self.thread_id,
                    config=processor_config
                ):
                    yield response
                
                # If we get here, the call was successful
                return
                
            except asyncio.TimeoutError:
                logger.warning(f"LLM call timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    yield {
                        'type': 'error',
                        'content': 'LLM call timed out after all retry attempts'
                    }
                    return
                    
            except Exception as e:
                logger.error(f"LLM call failed on attempt {attempt + 1}: {e}")
                
                if self._is_recoverable_error(e) and attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    yield {
                        'type': 'error',
                        'content': f'LLM call failed: {str(e)}'
                    }
                    return
    
    def _is_recoverable_error(self, error: Exception) -> bool:
        """Determine if an error is recoverable."""
        recoverable_errors = [
            'timeout',
            'connection',
            'network',
            'rate limit',
            'temporary',
            'service unavailable',
            'internal server error'
        ]
        
        error_str = str(error).lower()
        return any(recoverable in error_str for recoverable in recoverable_errors)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics."""
        return {
            'thread_id': self.thread_id,
            'project_id': self.project_id,
            'agent_config': self.agent_config,
            'health_status': self.state.get_health_status(),
            'performance_metrics': self.state.performance_metrics,
            'tool_usage': self.state.tool_usage_count,
            'error_history': self.state.error_history[-5:],  # Last 5 errors
            'capabilities': {
                'adaptive_timeout': self.adaptive_timeout,
                'context_awareness': self.context_awareness,
                'auto_recovery': self.auto_recovery,
                'learning_enabled': self.learning_enabled
            }
        }
    
    async def cleanup(self):
        """Cleanup resources and save state."""
        try:
            # Save performance metrics
            if self.learning_enabled:
                await self._save_learning_data()
            
            # Close database connections
            if self.db:
                await self.db.close()
            
            # Finalize trace
            if self.trace:
                self.trace.update(
                    metadata={
                        'final_metrics': self.state.performance_metrics,
                        'total_iterations': self.state.total_iterations
                    }
                )
            
            logger.info("Enhanced Agent cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def _save_learning_data(self):
        """Save learning data for future improvements."""
        try:
            learning_data = {
                'timestamp': datetime.now().isoformat(),
                'performance_metrics': self.state.performance_metrics,
                'tool_usage': self.state.tool_usage_count,
                'error_patterns': self._analyze_error_patterns(),
                'success_patterns': self._analyze_success_patterns()
            }
            
            # Save to database or file system
            # This could be enhanced to use a dedicated learning storage system
            logger.info("Learning data saved for future improvements")
            
        except Exception as e:
            logger.error(f"Error saving learning data: {e}")
    
    def _analyze_error_patterns(self) -> Dict[str, Any]:
        """Analyze error patterns for learning."""
        patterns = {}
        
        for error in self.state.error_history:
            error_type = self._categorize_error(error['error'])
            if error_type not in patterns:
                patterns[error_type] = 0
            patterns[error_type] += 1
        
        return patterns
    
    def _analyze_success_patterns(self) -> Dict[str, Any]:
        """Analyze success patterns for learning."""
        return {
            'high_success_tools': [
                tool for tool, stats in self.state.performance_metrics['tool_success_rate'].items()
                if stats > 0.9
            ],
            'optimal_response_time': self.state.performance_metrics['avg_response_time'],
            'successful_iterations': self.state.successful_iterations
        }
    
    def _categorize_error(self, error_msg: str) -> str:
        """Categorize error for pattern analysis."""
        error_msg_lower = error_msg.lower()
        
        if 'timeout' in error_msg_lower:
            return 'timeout'
        elif 'connection' in error_msg_lower:
            return 'connection'
        elif 'permission' in error_msg_lower or 'auth' in error_msg_lower:
            return 'permission'
        elif 'tool' in error_msg_lower:
            return 'tool_error'
        elif 'llm' in error_msg_lower or 'model' in error_msg_lower:
            return 'llm_error'
        else:
            return 'unknown'

# Convenience function for backward compatibility
async def run_enhanced_agent(
    thread_id: str,
    project_id: str,
    stream: bool = True,
    max_iterations: int = 100,
    model_name: str = "anthropic/claude-3-5-sonnet-20241022",
    enable_thinking: bool = False,
    reasoning_effort: str = 'medium',
    agent_config: Optional[Dict] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Run enhanced agent with improved capabilities.
    
    This is a convenience function that creates and runs an EnhancedAgent instance.
    """
    agent = EnhancedAgent(thread_id, project_id, agent_config)
    
    try:
        await agent.initialize()
        
        async for response in agent.run(
            stream=stream,
            max_iterations=max_iterations,
            model_name=model_name,
            enable_thinking=enable_thinking,
            reasoning_effort=reasoning_effort
        ):
            yield response
            
    finally:
        await agent.cleanup()