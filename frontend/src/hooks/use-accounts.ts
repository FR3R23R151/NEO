import useSWR, { SWRConfiguration } from 'swr';
import { createClient } from '@/lib/database/client';
import { GetAccountsResponse } from '@usebasejump/shared';

export const useAccounts = (options?: SWRConfiguration) => {
  const databaseClient = createClient();
  return useSWR<GetAccountsResponse>(
    !!databaseClient && ['accounts'],
    async () => {
      const { data, error } = await databaseClient.rpc('get_accounts');

      if (error) {
        throw new Error(error.message);
      }

      return data;
    },
    options,
  );
};
