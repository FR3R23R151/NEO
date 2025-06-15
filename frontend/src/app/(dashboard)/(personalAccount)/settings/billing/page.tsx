import { createClient } from '@/lib/database/server';
import AccountBillingStatus from '@/components/billing/account-billing-status';

const returnUrl = process.env.NEXT_PUBLIC_URL as string;

export default async function PersonalAccountBillingPage() {
  const databaseClient = await createClient();
  const { data: personalAccount } = await databaseClient.rpc(
    'get_personal_account',
  );

  return (
    <div>
      <AccountBillingStatus
        accountId={personalAccount.account_id}
        returnUrl={`${returnUrl}/settings/billing`}
      />
    </div>
  );
}
