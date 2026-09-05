import { beforeEach, describe, expect, it } from 'vitest'
import {
  clearRecentGroups,
  getRecentGroups,
  removeRecentGroup,
  saveRecentGroup,
} from './recentGroups'

const group = (id: string, name = 'Vacanza') => ({
  id,
  name,
  description: 'Estate',
  currency: 'EUR',
  status: 'active' as const,
  closing_count: 0,
  closing_balance_mode: 'separate' as const,
  created_at: '2026-08-26T12:00:00Z',
  members: [{ id: 1, name: 'Giulia' }],
  expenses: [],
})

describe('recentGroups', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('stores only minimal group metadata and refreshes an existing group', () => {
    saveRecentGroup(group('group-1', 'Prima'))
    saveRecentGroup(group('group-1', 'Aggiornata'))

    expect(getRecentGroups()).toEqual([
      expect.objectContaining({
        id: 'group-1',
        name: 'Aggiornata',
        memberCount: 1,
        expenseCount: 0,
      }),
    ])
    expect(JSON.stringify(getRecentGroups())).not.toContain('created_at')
  })

  it('keeps at most twenty groups and supports removal', () => {
    for (let index = 0; index < 21; index += 1) saveRecentGroup(group(`group-${index}`))

    expect(getRecentGroups()).toHaveLength(20)
    expect(removeRecentGroup('group-20')).toHaveLength(19)
    clearRecentGroups()
    expect(getRecentGroups()).toEqual([])
  })
})
