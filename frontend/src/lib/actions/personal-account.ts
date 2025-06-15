'use server';

import { createClient } from '../database/server';

export async function editPersonalAccountName(
  prevState: any,
  formData: FormData,
) {
  const name = formData.get('name') as string;
  const accountId = formData.get('accountId') as string;
  const database = await createClient();

  const { error } = await database.rpc('update_account', {
    name,
    account_id: accountId,
  });

  if (error) {
    return {
      message: error.message,
    };
  }
}
