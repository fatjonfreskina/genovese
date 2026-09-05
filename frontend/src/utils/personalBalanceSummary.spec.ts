import { describe, expect, it } from 'vitest'
import type { Balance, Settlement } from '../api/groups'
import {
  calculatePersonalBalanceSummary,
  calculatePersonalSettlementSummary,
  calculatePersonalBalancesByCurrency,
  calculatePersonalSettlementsByCurrency,
} from './personalBalanceSummary'

const balances: Balance[] = [
  {
    from_member_id: 1,
    from_member_name: 'Marco',
    to_member_id: 2,
    to_member_name: 'Giulia',
    amount: '20.50',
    currency: 'EUR',
  },
  {
    from_member_id: 3,
    from_member_name: 'Luca',
    to_member_id: 1,
    to_member_name: 'Marco',
    amount: '8.25',
    currency: 'EUR',
  },
  {
    from_member_id: 3,
    from_member_name: 'Luca',
    to_member_id: 2,
    to_member_name: 'Giulia',
    amount: '4.00',
    currency: 'EUR',
  },
]

describe('calculatePersonalBalanceSummary', () => {
  it('calculates incoming, outgoing and net amounts for the selected member', () => {
    expect(calculatePersonalBalanceSummary(balances, 1)).toEqual({
      amountToPay: 20.5,
      amountToReceive: 8.25,
      netAmount: -12.25,
      outgoingPayments: 1,
      incomingPayments: 1,
    })
  })

  it('returns an empty summary for a member without payments', () => {
    expect(calculatePersonalBalanceSummary(balances, 99)).toEqual({
      amountToPay: 0,
      amountToReceive: 0,
      netAmount: 0,
      outgoingPayments: 0,
      incomingPayments: 0,
    })
  })
})

describe('calculatePersonalSettlementSummary', () => {
  it('excludes confirmed and cancelled payments from the personal summary', () => {
    const settlements: Settlement[] = [
      {
        id: 1,
        from_member_id: 1,
        to_member_id: 2,
        amount: '20.50',
        currency: 'EUR',
        status: 'pending',
      },
      {
        id: 2,
        from_member_id: 3,
        to_member_id: 1,
        amount: '8.25',
        currency: 'EUR',
        status: 'confirmed',
      },
      {
        id: 3,
        from_member_id: 1,
        to_member_id: 3,
        amount: '4.00',
        currency: 'EUR',
        status: 'cancelled',
      },
    ]

    expect(calculatePersonalSettlementSummary(settlements, 1)).toEqual({
      amountToPay: 20.5,
      amountToReceive: 0,
      netAmount: -20.5,
      outgoingPayments: 1,
      incomingPayments: 0,
    })
  })
})

describe('personal summaries by currency', () => {
  it('does not offset a debt in EUR with a credit in another currency', () => {
    expect(
      calculatePersonalBalancesByCurrency(
        [balances[0]!, { ...balances[1]!, currency: 'ALL', amount: '2000' }],
        1,
        'EUR',
      ),
    ).toEqual([
      {
        currency: 'EUR',
        amountToPay: 20.5,
        amountToReceive: 0,
        netAmount: -20.5,
        outgoingPayments: 1,
        incomingPayments: 0,
      },
      {
        currency: 'ALL',
        amountToPay: 0,
        amountToReceive: 2000,
        netAmount: 2000,
        outgoingPayments: 0,
        incomingPayments: 1,
      },
    ])
  })

  it('retains a zero summary in a settled currency and excludes cancelled history', () => {
    const result = calculatePersonalSettlementsByCurrency(
      [
        {
          id: 1,
          from_member_id: 1,
          to_member_id: 2,
          amount: '10',
          currency: 'JPY',
          status: 'confirmed',
        },
        {
          id: 2,
          from_member_id: 1,
          to_member_id: 2,
          amount: '20',
          currency: 'USD',
          status: 'cancelled',
        },
      ],
      1,
      'EUR',
    )
    expect(result).toEqual([
      {
        currency: 'JPY',
        amountToPay: 0,
        amountToReceive: 0,
        netAmount: 0,
        outgoingPayments: 0,
        incomingPayments: 0,
      },
    ])
    expect(calculatePersonalBalancesByCurrency([], 1, 'EUR')[0]?.currency).toBe('EUR')
  })

  it('sums cents without floating-point artifacts', () => {
    const result = calculatePersonalBalanceSummary(
      [
        { ...balances[0]!, amount: '0.10' },
        { ...balances[0]!, amount: '0.20' },
      ],
      1,
    )
    expect(result.amountToPay).toBe(0.3)
    expect(result.netAmount).toBe(-0.3)
  })
})
