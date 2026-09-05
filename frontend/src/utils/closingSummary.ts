import type { Balance, Group } from '../api/groups'
import { expenseTotalsByCurrency, formatCurrency } from './currency'

export function buildClosingSummary(group: Group, balances: Balance[], groupLink: string): string {
  const totals = expenseTotalsByCurrency(group.expenses, group.currency)
  const totalLines =
    totals.length === 1
      ? [`💰 Totale spese: ${formatCurrency(totals[0]!.amount, totals[0]!.currency)}`]
      : [
          '💰 Totali spese per valuta:',
          ...totals.map(
            (total) => `• ${total.currency}: ${formatCurrency(total.amount, total.currency)}`,
          ),
        ]
  const unified = group.closing_balance_mode === 'unified'
  const hasForeignExpenses = group.expenses.some(
    (expense) => expense.currency && expense.currency !== group.currency,
  )
  if (unified && hasForeignExpenses) {
    const convertedAmounts = group.expenses.map((expense) =>
      !expense.currency || expense.currency === group.currency
        ? Number(expense.amount)
        : expense.converted_amount == null
          ? null
          : Number(expense.converted_amount),
    )
    if (convertedAmounts.every((amount) => amount !== null && Number.isFinite(amount))) {
      const convertedCents = convertedAmounts.reduce(
        (sum: number, amount) => sum + Math.round(amount! * 100),
        0,
      )
      totalLines.push(
        `💱 Totale unificato: ${formatCurrency(convertedCents / 100, group.currency)}`,
      )
    }
    totalLines.push('Cambi salvati sulle singole spese, fissati per questa chiusura.')
  }
  const payments = balances.length
    ? balances.map(
        (balance) =>
          `• ${balance.from_member_name} deve ${formatCurrency(balance.amount, balance.currency || group.currency)} a ${balance.to_member_name}`,
      )
    : ['• Nessun pagamento necessario: i conti sono già in pari 🎉']
  const version = group.closing_count > 1 ? ` - versione ${group.closing_count}` : ''

  return [
    `🧾 Riepilogo conti - ${group.name}${version}`,
    '',
    ...totalLines,
    `👥 Partecipanti: ${group.members.length}`,
    '',
    '💸 Pagamenti da effettuare:',
    ...payments,
    '',
    '🔒 Il gruppo è ora in chiusura: spese e partecipanti sono bloccati.',
    '🔗 Apri Equa per segnalare un pagamento o confermare una ricezione:',
    groupLink,
  ].join('\n')
}
