import client from './client'

export interface Member {
  id: number
  name: string
  email?: string
}

export interface Split {
  member_id: number
  share_amount: number | string
}

export type BalanceMode = 'separate' | 'unified'
export type ExchangeRateSource = 'identity' | 'frankfurter' | 'manual'

export interface ExchangeRate {
  currency: string
  target_currency: string
  rate: string
  date: string
  source: ExchangeRateSource
}

export interface ExpenseInput {
  paid_by_member_id: number
  description: string
  amount: number
  currency?: string
  expense_date?: string
  exchange_rate?: number | string
  refresh_exchange_rate?: boolean
}

export interface Expense {
  id: number
  paid_by_member_id: number
  description: string
  amount: number | string
  currency: string
  expense_date: string
  exchange_rate: string | null
  exchange_rate_date: string | null
  exchange_rate_source: ExchangeRateSource | null
  converted_amount: string | null
  created_at: string
  splits: Split[]
}

export interface Group {
  id: string
  name: string
  description?: string
  currency: string
  status: 'active' | 'closing' | 'closed'
  closing_count: number
  closing_balance_mode: BalanceMode
  created_at: string
  members: Member[]
  expenses: Expense[]
}

export interface Balance {
  currency: string
  from_member_id: number
  from_member_name: string
  to_member_id: number
  to_member_name: string
  amount: string
}

export interface Settlement {
  currency: string
  id: number
  from_member_id: number
  to_member_id: number
  amount: string
  status: 'pending' | 'confirmed' | 'cancelled'
  reported_by_member_id?: number | null
  reported_at?: string | null
  confirmed_by_member_id?: number | null
  confirmed_at?: string | null
}

export const groupsApi = {
  create: (data: {
    name: string
    description?: string
    currency: string
    members: { name: string; email?: string }[]
  }) => client.post<Group>('/groups/', data),

  get: (id: string) => client.get<Group>(`/groups/${id}`),

  updateStatus: (id: string, status: Group['status'], balanceMode?: BalanceMode) =>
    client.patch<Group>(`/groups/${id}/status`, {
      status,
      ...(status === 'closing' && balanceMode ? { balance_mode: balanceMode } : {}),
    }),

  delete: (id: string) => client.delete(`/groups/${id}`),

  getBalances: (id: string, mode: BalanceMode = 'separate') =>
    client.get<Balance[]>(`/groups/${id}/balances/`, { params: { mode } }),

  getExchangeRate: (id: string, currency: string, expenseDate: string) =>
    client.get<ExchangeRate>(`/groups/${id}/exchange-rate`, {
      params: { currency, expense_date: expenseDate },
    }),

  getSettlements: (id: string) => client.get<Settlement[]>(`/groups/${id}/settlements/`),

  reportSettlement: (groupId: string, settlementId: number, memberId: number) =>
    client.patch<Settlement>(`/groups/${groupId}/settlements/${settlementId}/report`, {
      member_id: memberId,
    }),

  confirmSettlement: (groupId: string, settlementId: number, memberId: number) =>
    client.patch<Settlement>(`/groups/${groupId}/settlements/${settlementId}/confirm`, {
      member_id: memberId,
    }),

  addExpenseEqual: (groupId: string, data: ExpenseInput) =>
    client.post<Expense>(`/groups/${groupId}/expenses/equal`, data),

  addExpenseSubset: (groupId: string, data: ExpenseInput & { member_ids: number[] }) =>
    client.post<Expense>(`/groups/${groupId}/expenses/subset`, data),

  addExpense: (groupId: string, data: ExpenseInput & { splits: Split[] }) =>
    client.post<Expense>(`/groups/${groupId}/expenses/`, data),

  updateExpense: (groupId: string, expenseId: number, data: ExpenseInput & { splits: Split[] }) =>
    client.put<Expense>(`/groups/${groupId}/expenses/${expenseId}`, data),

  deleteMember: (groupId: string, memberId: number) =>
    client.delete(`/groups/${groupId}/members/${memberId}`),

  deleteExpense: (groupId: string, expenseId: number) =>
    client.delete(`/groups/${groupId}/expenses/${expenseId}`),

  addMember: (groupId: string, data: { name: string; email?: string }) =>
    client.post<Member>(`/groups/${groupId}/members/`, data),

  updateMember: (groupId: string, memberId: number, data: { name?: string; email?: string }) =>
    client.patch<Member>(`/groups/${groupId}/members/${memberId}`, data),
}
