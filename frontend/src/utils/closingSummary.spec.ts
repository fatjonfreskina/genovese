import { describe, expect, it } from 'vitest'
import type { Balance, Group } from '../api/groups'
import { buildClosingSummary } from './closingSummary'
import { formatCurrency } from './currency'

const group: Group = {
  id: 'group-1',
  name: 'Weekend',
  currency: 'EUR',
  status: 'closing',
  closing_count: 1,
  closing_balance_mode: 'separate',
  created_at: '2026-08-28T12:00:00Z',
  members: [
    { id: 1, name: 'Giulia' },
    { id: 2, name: 'Marco' },
  ],
  expenses: [
    {
      id: 1,
      paid_by_member_id: 1,
      description: 'Cena',
      amount: 42.5,
      currency: 'EUR',
      expense_date: '2026-08-28',
      exchange_rate: '1',
      exchange_rate_date: '2026-08-28',
      exchange_rate_source: 'identity',
      converted_amount: '42.50',
      created_at: '2026-08-28T18:00:00Z',
      splits: [],
    },
  ],
}

describe('buildClosingSummary', () => {
  it('includes totals, payments and the group link', () => {
    const balances: Balance[] = [
      {
        from_member_id: 2,
        from_member_name: 'Marco',
        to_member_id: 1,
        to_member_name: 'Giulia',
        amount: '21.25',
        currency: 'EUR',
      },
    ]

    const summary = buildClosingSummary(group, balances, 'https://equa.example/group/group-1')

    expect(summary).toContain('🧾 Riepilogo conti - Weekend')
    expect(summary).toContain('Totale spese: 42,50')
    expect(summary).toContain('Marco deve 21,25')
    expect(summary).toContain('https://equa.example/group/group-1')
    expect(summary).not.toContain('versione 1')
  })

  it('labels later closing cycles with their version', () => {
    const summary = buildClosingSummary({ ...group, closing_count: 2 }, [], 'https://equa.example')

    expect(summary).toContain('Riepilogo conti - Weekend - versione 2')
  })

  it('explains when no payment is required', () => {
    expect(buildClosingSummary(group, [], 'https://equa.example')).toContain(
      'Nessun pagamento necessario',
    )
  })

  it('keeps expense totals and payments in their original currencies', () => {
    const multicurrency: Group = {
      ...group,
      expenses: [
        group.expenses[0]!,
        { ...group.expenses[0]!, id: 2, currency: 'ALL', amount: 1000, converted_amount: '10.80' },
      ],
    }
    const summary = buildClosingSummary(
      multicurrency,
      [
        {
          from_member_id: 2,
          from_member_name: 'Marco',
          to_member_id: 1,
          to_member_name: 'Giulia',
          amount: '500',
          currency: 'ALL',
        },
      ],
      'https://equa.example',
    )
    expect(summary).toContain('Totali spese per valuta:')
    expect(summary).toContain('EUR: 42,50')
    expect(summary).toContain(`ALL: ${formatCurrency(1000, 'ALL')}`)
    expect(summary).toContain('Marco deve 500,00')
    expect(summary).not.toContain('1.042,50')
  })

  it('includes the saved converted total only for a complete unified closing', () => {
    const multicurrency: Group = {
      ...group,
      closing_balance_mode: 'unified',
      expenses: [
        group.expenses[0]!,
        { ...group.expenses[0]!, id: 2, currency: 'JPY', amount: 1000, converted_amount: '6.20' },
      ],
    }
    expect(buildClosingSummary(multicurrency, [], '')).toContain('Totale unificato: 48,70')
    multicurrency.expenses[1]!.converted_amount = null
    expect(buildClosingSummary(multicurrency, [], '')).not.toContain('Totale unificato:')
  })
})
