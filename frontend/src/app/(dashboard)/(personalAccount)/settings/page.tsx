import EditPersonalAccountName from '@/components/basejump/edit-personal-account-name';
import { createClient } from '@/lib/database/server';

export default async function PersonalAccountSettingsPage() {
  const databaseClient = await createClient();
  const { data: personalAccount } = await databaseClient.rpc(
    'get_personal_account',
  );

  return (
    <div>
      <EditPersonalAccountName account={personalAccount} />
    </div>
  );
}
