import client from './client'

export interface Member {
  id: number
  name: string
  email?: string
}

export interface Split {
  member_id: number
  share_amount: number
}

export interface Expense {
  id: number
  paid_by_member_id: number
  description: string
  amount: number
  created_at: string
  splits: Split[]
}

export interface Group {
  id: string
  name: string
  description?: string
  currency: string
  created_at: string
  members: Member[]
  expenses: Expense[]
}

export interface Balance {
  from_member_id: number
  from_member_name: string
  to_member_id: number
  to_member_name: string
  amount: string
}

export const groupsApi = {
  create: (data: {
    name: string
    description?: string
    currency: string
    members: { name: string; email?: string }[]
  }) => client.post<Group>('/groups/', data),

  get: (id: string) => client.get<Group>(`/groups/${id}`),

  delete: (id: string) => client.delete(`/groups/${id}`),

  getBalances: (id: string) => client.get<Balance[]>(`/groups/${id}/balances/`),

  addExpenseEqual: (groupId: string, data: {
    paid_by_member_id: number
    description: string
    amount: number
  }) => client.post<Expense>(`/groups/${groupId}/expenses/equal`, data),

  addExpenseSubset: (groupId: string, data: {
    paid_by_member_id: number
    description: string
    amount: number
    member_ids: number[]
  }) => client.post<Expense>(`/groups/${groupId}/expenses/subset`, data),

  addExpense: (groupId: string, data: {
    paid_by_member_id: number
    description: string
    amount: number
    splits: Split[]
  }) => client.post<Expense>(`/groups/${groupId}/expenses/`, data),

  deleteExpense: (groupId: string, expenseId: number) =>
    client.delete(`/groups/${groupId}/expenses/${expenseId}`),
}