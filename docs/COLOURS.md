# Colours

All chart colours live in `dashboard/src/utils/chartTheme.js`. A test fails if a component writes a hex value.

| Token | Hex | Use |
|---|---|---|
| `gain` | #2C7A7B (primary-600) | Support, a fall in bills |
| `loss` | #9CA3AF (gray-400) | A rise in bills |
| `neutral` | #6B7280 (gray-500) | Neutral marks |
| `restated` | #D1D5DB (gray-300) | Cap levels on the earlier typical-consumption basis |
| `series[0]`, `series[1]` | #285E61, #4FD1C5 | Two-series charts (after support; second scenario) |
| `grid`, `axis` | #E2E8F0, #4B5563 | Grid lines and axis text |

No tick badges on selected chips: selection shows as fill and border only.
