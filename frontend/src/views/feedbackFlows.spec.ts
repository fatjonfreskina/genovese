import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { createApp, nextTick, type App, type Component } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import HomeView from './HomeView.vue'
import GroupView from './GroupView.vue'
import { groupsApi, type Group } from '../api/groups'
import { getRecentGroups, saveRecentGroup } from '../utils/recentGroups'

vi.mock('../utils/analytics', () => ({ trackEvent: vi.fn() }))
vi.mock('../api/groups', () => ({
  groupsApi: {
    get: vi.fn(),
    deleteExpense: vi.fn(),
    deleteMember: vi.fn(),
    getBalances: vi.fn(),
    getSettlements: vi.fn(),
    getExchangeRate: vi.fn(),
    addExpenseEqual: vi.fn(),
    updateStatus: vi.fn(),
  },
}))

let app: App | undefined
const group: Group = {
  id: 'test-group',
  name: 'Vacanza',
  currency: 'EUR',
  status: 'active',
  closing_count: 0,
  closing_balance_mode: 'separate',
  created_at: '2026-09-02',
  members: [
    { id: 1, name: 'Anna' },
    { id: 2, name: 'Luca' },
  ],
  expenses: [
    {
      id: 10,
      description: 'Cena',
      amount: 20,
      currency: 'EUR',
      expense_date: '2026-09-02',
      exchange_rate: '1',
      exchange_rate_date: '2026-09-02',
      exchange_rate_source: 'identity',
      converted_amount: '20.00',
      paid_by_member_id: 1,
      created_at: '2026-09-02',
      splits: [],
    },
  ],
}

async function flush() {
  for (let step = 0; step < 6; step++) await nextTick()
}

async function mount(view: Component, path = '/group/test-group') {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: view },
      { path: '/group/:id', component: view },
    ],
  })
  await router.push(path)
  const container = document.createElement('div')
  document.body.append(container)
  app = createApp(view).use(router)
  app.mount(container)
  await flush()
}

async function click(text: string) {
  const button = [...document.querySelectorAll('button')].find(
    (item) => item.textContent?.trim() === text,
  )
  expect(button, `Missing button: ${text}`).toBeDefined()
  button!.click()
  await flush()
}

beforeEach(() => {
  vi.clearAllMocks()
  localStorage.clear()
  Object.defineProperties(HTMLDialogElement.prototype, {
    showModal: {
      configurable: true,
      value: function (this: HTMLDialogElement) {
        this.open = true
      },
    },
    close: {
      configurable: true,
      value: function (this: HTMLDialogElement) {
        this.open = false
      },
    },
  })
  vi.mocked(groupsApi.get).mockResolvedValue({ data: structuredClone(group) } as never)
  vi.mocked(groupsApi.getBalances).mockResolvedValue({ data: [] } as never)
  vi.mocked(groupsApi.getSettlements).mockResolvedValue({ data: [] } as never)
  vi.mocked(groupsApi.getExchangeRate).mockResolvedValue({
    data: {
      currency: 'ALL',
      target_currency: 'EUR',
      rate: '0.01',
      date: '2026-09-02',
      source: 'frankfurter',
    },
  } as never)
  vi.mocked(groupsApi.addExpenseEqual).mockResolvedValue({} as never)
  vi.mocked(groupsApi.deleteExpense).mockResolvedValue({} as never)
  vi.mocked(groupsApi.deleteMember).mockResolvedValue({} as never)
})

afterEach(() => {
  app?.unmount()
  app = undefined
  document.body.replaceChildren()
  localStorage.clear()
})

it('clears only local history and only after confirmation', async () => {
  saveRecentGroup(group)
  await mount(HomeView, '/')
  await click('Cancella tutto')
  await click('Annulla')
  expect(getRecentGroups()).toHaveLength(1)
  await click('Cancella tutto')
  await click('Cancella cronologia')
  expect(getRecentGroups()).toHaveLength(0)
})

it('deletes the named expense only after confirmation and shows API failures', async () => {
  await mount(GroupView)
  const remove = document.querySelector<HTMLButtonElement>('[aria-label="Elimina spesa Cena"]')!
  remove.focus()
  remove.click()
  await flush()
  expect(document.querySelector('dialog')?.textContent).toContain('Cena')
  expect(groupsApi.deleteExpense).not.toHaveBeenCalled()
  await click('Annulla')
  expect(groupsApi.deleteExpense).not.toHaveBeenCalled()
  expect(document.activeElement).toBe(remove)
  vi.mocked(groupsApi.deleteExpense).mockRejectedValueOnce(new Error('offline'))
  remove.click()
  await flush()
  await click('Elimina spesa')
  expect(groupsApi.deleteExpense).toHaveBeenCalledExactlyOnceWith('test-group', 10)
  expect(document.querySelector('dialog')?.textContent).toContain('Spesa non eliminata')
  await click('Ho capito')
  expect(remove.disabled).toBe(false)
})

it('keeps member deletion behind confirmation and displays backend constraints', async () => {
  await mount(GroupView)
  await click('👥 Partecipanti')
  const remove = document.querySelector<HTMLButtonElement>(
    '[aria-label="Rimuovi partecipante Anna"]',
  )!
  remove.click()
  await flush()
  await click('Annulla')
  expect(groupsApi.deleteMember).not.toHaveBeenCalled()
  vi.mocked(groupsApi.deleteMember).mockRejectedValueOnce({
    response: { data: { detail: 'Il partecipante ha spese.' } },
  })
  remove.click()
  await flush()
  await click('Rimuovi partecipante')
  expect(groupsApi.deleteMember).toHaveBeenCalledExactlyOnceWith('test-group', 1)
  expect(document.querySelector('dialog')?.textContent).toContain('Il partecipante ha spese.')
})

it('keeps multi-currency details progressive and closes with the selected balance mode', async () => {
  const foreignExpense = {
    ...group.expenses[0]!,
    id: 11,
    description: 'Taxi',
    currency: 'ALL',
    amount: 1000,
    exchange_rate: '0.01',
    exchange_rate_date: '2026-09-02',
    exchange_rate_source: 'frankfurter' as const,
    converted_amount: '10.00',
  }
  vi.mocked(groupsApi.get).mockResolvedValue({
    data: { ...group, expenses: [...group.expenses, foreignExpense] },
  } as never)
  vi.mocked(groupsApi.updateStatus).mockResolvedValue({
    data: {
      ...group,
      status: 'closing',
      closing_balance_mode: 'unified',
      expenses: [...group.expenses, foreignExpense],
    },
  } as never)

  await mount(GroupView)
  await click('⚖️ Bilanci')
  expect(groupsApi.getBalances).toHaveBeenCalledWith('test-group', 'separate')
  await click('Unifica in EUR')
  expect(groupsApi.getBalances).toHaveBeenLastCalledWith('test-group', 'unified')
  expect(document.body.textContent).toContain('Totale convertito:')

  await click('Chiudiamo i conti')
  expect(document.querySelector('dialog')?.textContent).toContain(
    'I pagamenti saranno fissati in EUR',
  )
  await click('Inizia chiusura')
  expect(groupsApi.updateStatus).toHaveBeenCalledWith('test-group', 'closing', 'unified')
})

it.each([
  ['closing', 'Segna come chiuso', 'Chiudi gruppo', 'closed'],
  ['closed', 'Riapri conti', 'Riapri conti', 'active'],
] as const)('confirms status changes from %s', async (status, trigger, confirm, expected) => {
  vi.mocked(groupsApi.get).mockResolvedValue({ data: { ...group, status } } as never)
  vi.mocked(groupsApi.updateStatus).mockResolvedValue({
    data: { ...group, status: expected },
  } as never)
  await mount(GroupView)
  await click(trigger)
  await click('Annulla')
  expect(groupsApi.updateStatus).not.toHaveBeenCalled()
  await click(trigger)
  const buttons = [...document.querySelectorAll<HTMLButtonElement>('dialog button')]
  buttons.find((item) => item.textContent?.trim() === confirm)!.click()
  await flush()
  expect(groupsApi.updateStatus).toHaveBeenCalledExactlyOnceWith('test-group', expected)
})
