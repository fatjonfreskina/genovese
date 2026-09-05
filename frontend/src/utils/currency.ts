export interface CurrencyOption {
  code: string
  name: string
  decimals: number
}

export const CURRENCIES: readonly CurrencyOption[] = [
  { code: 'EUR', name: 'Euro', decimals: 2 },
  { code: 'USD', name: 'Dollaro statunitense', decimals: 2 },
  { code: 'GBP', name: 'Sterlina britannica', decimals: 2 },
  { code: 'CHF', name: 'Franco svizzero', decimals: 2 },
  { code: 'ALL', name: 'Lek albanese', decimals: 2 },
  { code: 'JPY', name: 'Yen giapponese', decimals: 0 },
  { code: 'CAD', name: 'Dollaro canadese', decimals: 2 },
  { code: 'AUD', name: 'Dollaro australiano', decimals: 2 },
  { code: 'NZD', name: 'Dollaro neozelandese', decimals: 2 },
  { code: 'CNY', name: 'Yuan cinese', decimals: 2 },
  { code: 'HKD', name: 'Dollaro di Hong Kong', decimals: 2 },
  { code: 'SGD', name: 'Dollaro di Singapore', decimals: 2 },
  { code: 'INR', name: 'Rupia indiana', decimals: 2 },
  { code: 'THB', name: 'Baht thailandese', decimals: 2 },
  { code: 'IDR', name: 'Rupia indonesiana', decimals: 2 },
  { code: 'MYR', name: 'Ringgit malese', decimals: 2 },
  { code: 'PHP', name: 'Peso filippino', decimals: 2 },
  { code: 'KRW', name: 'Won sudcoreano', decimals: 0 },
  { code: 'VND', name: 'Dong vietnamita', decimals: 0 },
  { code: 'AED', name: 'Dirham degli Emirati Arabi', decimals: 2 },
  { code: 'SAR', name: 'Riyal saudita', decimals: 2 },
  { code: 'TRY', name: 'Lira turca', decimals: 2 },
  { code: 'SEK', name: 'Corona svedese', decimals: 2 },
  { code: 'NOK', name: 'Corona norvegese', decimals: 2 },
  { code: 'DKK', name: 'Corona danese', decimals: 2 },
  { code: 'PLN', name: 'Złoty polacco', decimals: 2 },
  { code: 'CZK', name: 'Corona ceca', decimals: 2 },
  { code: 'HUF', name: 'Fiorino ungherese', decimals: 2 },
  { code: 'RON', name: 'Leu romeno', decimals: 2 },
  { code: 'BGN', name: 'Lev bulgaro', decimals: 2 },
  { code: 'BRL', name: 'Real brasiliano', decimals: 2 },
  { code: 'MXN', name: 'Peso messicano', decimals: 2 },
  { code: 'ZAR', name: 'Rand sudafricano', decimals: 2 },
  { code: 'CLP', name: 'Peso cileno', decimals: 0 },
  { code: 'ISK', name: 'Corona islandese', decimals: 0 },
]

export function currencyDecimals(currency: string): number {
  return CURRENCIES.find((item) => item.code === currency)?.decimals ?? 2
}

export function currencyStep(currency: string): number {
  return 10 ** -currencyDecimals(currency)
}

export function formatCurrency(amount: number | string, currency: string): string {
  return new Intl.NumberFormat('it-IT', {
    style: 'currency',
    currency,
    minimumFractionDigits: currencyDecimals(currency),
    maximumFractionDigits: currencyDecimals(currency),
  }).format(Number(amount))
}

export function todayDate(): string {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
}

export interface CurrencyTotal {
  currency: string
  amount: number
}

export function expenseTotalsByCurrency(
  expenses: readonly { amount: number | string; currency?: string }[],
  defaultCurrency: string,
): CurrencyTotal[] {
  const totals = new Map<string, number>()
  for (const expense of expenses) {
    const currency = expense.currency || defaultCurrency
    // All supported currencies have at most two decimal places. Sum integer cents.
    totals.set(currency, (totals.get(currency) ?? 0) + Math.round(Number(expense.amount) * 100))
  }
  if (!totals.size) totals.set(defaultCurrency, 0)
  return [...totals.entries()]
    .sort(([a], [b]) => compareCurrencies(a, b, defaultCurrency))
    .map(([currency, cents]) => ({ currency, amount: cents / 100 }))
}

export function compareCurrencies(a: string, b: string, defaultCurrency: string): number {
  if (a === b) return 0
  if (a === defaultCurrency) return -1
  if (b === defaultCurrency) return 1
  return a.localeCompare(b)
}
