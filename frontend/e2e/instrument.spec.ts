import { expect, test } from '@playwright/test'

test.beforeEach(async ({ request }) => {
  await request.post('http://localhost:8000/api/instruments/laser-001/disconnect')
})

test('connect instrument and see connected status', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('laser-001')).toBeVisible()
  await page.getByRole('button', { name: /^Connect$/ }).click()
  await expect(page.getByText('connected').first()).toBeVisible()
  await expect(page.getByRole('button', { name: /^Disconnect$/ })).toBeVisible()
})

test('send SCPI commands and see responses', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: /^Connect$/ }).click()
  await expect(page.getByRole('button', { name: /^Disconnect$/ })).toBeVisible()

  const input = page.locator('.console-input')

  // Enable output
  await input.fill('OUTP ON')
  await input.press('Enter')
  await expect(page.locator('.history-res').first()).toHaveText('OK', { timeout: 5000 })

  // Read power measurement
  await input.fill('MEAS:POW?')
  await input.press('Enter')
  await expect(page.locator('.history-res').nth(1)).toContainText(/[-\d.]/, { timeout: 5000 })
})

test('firmware upgrade shows progress and completes', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: /^Connect$/ }).click()
  await expect(page.getByRole('button', { name: /^Upgrade Firmware$/ })).toBeVisible()

  await page.getByRole('button', { name: /^Upgrade Firmware$/ }).click()

  // Progress state should appear (uploading / validating / applying)
  await expect(page.locator('.badge-yellow').first()).toBeVisible({ timeout: 3000 })

  // Eventually reaches completed
  await expect(
    page.locator('.badge-green').last(),
  ).toBeVisible({ timeout: 10000 })
})
