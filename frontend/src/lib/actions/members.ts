'use server';

import { redirect } from 'next/navigation';
import { createClient } from '../database/server';

export async function removeTeamMember(prevState: any, formData: FormData) {
  const userId = formData.get('userId') as string;
  const accountId = formData.get('accountId') as string;
  const returnUrl = formData.get('returnUrl') as string;
  const database = await createClient();

  const { error } = await database.rpc('remove_account_member', {
    user_id: userId,
    account_id: accountId,
  });

  if (error) {
    return {
      message: error.message,
    };
  }

  redirect(returnUrl);
}

export async function updateTeamMemberRole(prevState: any, formData: FormData) {
  const userId = formData.get('userId') as string;
  const accountId = formData.get('accountId') as string;
  const newAccountRole = formData.get('accountRole') as string;
  const returnUrl = formData.get('returnUrl') as string;
  const makePrimaryOwner = formData.get('makePrimaryOwner');

  const database = await createClient();

  const { error } = await database.rpc('update_account_user_role', {
    user_id: userId,
    account_id: accountId,
    new_account_role: newAccountRole,
    make_primary_owner: makePrimaryOwner,
  });

  if (error) {
    return {
      message: error.message,
    };
  }

  redirect(returnUrl);
}
