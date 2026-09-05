import type { Balance, Settlement } from '../api/groups'
import { compareCurrencies } from './currency'

export interface PersonalBalanceSummary {
  amountToPay: number
  amountToReceive: number
  netAmount: number
  outgoingPayments: number
  incomingPayments: number
}

export function calculatePersonalBalanceSummary(
  balances: Balance[],
  memberId: number,
): PersonalBalanceSummary {
  const personalBalances = balances.reduce(
    (summary, balance) => {
      const amount = Number(balance.amount)
      if (balance.from_member_id === memberId) {
        summary.amountToPay = Math.round((summary.amountToPay + amount) * 100) / 100
        summary.outgoingPayments += 1
      }
      if (balance.to_member_id === memberId) {
        summary.amountToReceive = Math.round((summary.amountToReceive + amount) * 100) / 100
        summary.incomingPayments += 1
      }
      return summary
    },
    {
      amountToPay: 0,
      amountToReceive: 0,
      outgoingPayments: 0,
      incomingPayments: 0,
    },
  )

  return {
    ...personalBalances,
    netAmount:
      Math.round((personalBalances.amountToReceive - personalBalances.amountToPay) * 100) / 100,
  }
}

export function calculatePersonalSettlementSummary(
  settlements: Settlement[],
  memberId: number,
): PersonalBalanceSummary {
  const pendingBalances: Balance[] = settlements
    .filter((settlement) => settlement.status === 'pending')
    .map((settlement) => ({
      from_member_id: settlement.from_member_id,
      from_member_name: '',
      to_member_id: settlement.to_member_id,
      to_member_name: '',
      amount: settlement.amount,
      currency: settlement.currency,
    }))

  return calculatePersonalBalanceSummary(pendingBalances, memberId)
}

export interface PersonalCurrencySummary extends PersonalBalanceSummary {
  currency: string
}

export function calculatePersonalBalancesByCurrency(
  balances: Balance[],
  memberId: number,
  defaultCurrency: string,
): PersonalCurrencySummary[] {
  const currencies = new Set(balances.map((balance) => balance.currency || defaultCurrency))
  if (!currencies.size) currencies.add(defaultCurrency)
  return [...currencies]
    .sort((a, b) => compareCurrencies(a, b, defaultCurrency))
    .map((currency) => ({
      currency,
      ...calculatePersonalBalanceSummary(
        balances.filter((balance) => (balance.currency || defaultCurrency) === currency),
        memberId,
      ),
    }))
}

export function calculatePersonalSettlementsByCurrency(
  settlements: Settlement[],
  memberId: number,
  defaultCurrency: string,
): PersonalCurrencySummary[] {
  const currencies = new Set(
    settlements
      .filter((settlement) => settlement.status !== 'cancelled')
      .map((settlement) => settlement.currency || defaultCurrency),
  )
  if (!currencies.size) currencies.add(defaultCurrency)
  return [...currencies]
    .sort((a, b) => compareCurrencies(a, b, defaultCurrency))
    .map((currency) => ({
      currency,
      ...calculatePersonalSettlementSummary(
        settlements.filter((settlement) => (settlement.currency || defaultCurrency) === currency),
        memberId,
      ),
    }))
}
