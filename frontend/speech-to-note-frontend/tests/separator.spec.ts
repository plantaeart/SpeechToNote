// Throwaway check: does <Separator /> fall back to a usable default height?
// Run with: npx vitest run tests/separator.spec.ts
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import Separator from '@/components/styles/Separator.vue'

describe('Separator', () => {
  it('renders a non-empty default height when no prop is given', () => {
    const wrapper = mount(Separator)
    const style = wrapper.attributes('style') ?? ''
    expect(style).toMatch(/height:\s*[^;]+/)
    // The default must be a real value, not the string "undefined".
    expect(style).not.toMatch(/undefined|:\s*;/)
  })

  it('honours an explicit height prop', () => {
    const wrapper = mount(Separator, { props: { height: '1rem' } })
    expect(wrapper.attributes('style')).toContain('1rem')
  })
})