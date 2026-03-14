# Phase 4 Tasks — UI Polish

## Goal
The dashboard should feel like a real prediction market product, not a data panel.

## Tasks

### F4.1 — Chart Polish
- [ ] Dark background chart with subtle grid lines
- [ ] Probability line color shifts: green above 55%, amber 40–55%, red below 40%
- [ ] Animated line drawing as new points arrive
- [ ] Custom tooltip: trade number, agent name, direction, probability
- [ ] Reference line at 50%

### F4.2 — Agent Cards
- [ ] Compact card design with clear visual hierarchy
- [ ] Agent type icon or badge (Specialist / Hybrid / Master)
- [ ] Last trade indicator (direction + delta)
- [ ] Category dots or mini-badges showing knowledge breadth
- [ ] Subtle animation on card update

### F4.3 — Trade Feed
- [ ] Slide-in animation for new trade entries
- [ ] Color-coded rows: green for BUY, red for SELL
- [ ] Compact layout: timestamp left, explanation right
- [ ] Agent name clickable (opens drawer)

### F4.4 — Probability Display
- [ ] Large bold number with % sign
- [ ] Trend arrow (up/down/flat) with delta since last 5 trades
- [ ] Color: green/amber/red based on threshold
- [ ] Subtle pulse animation on update

### F4.5 — Agent Drawer
- [ ] Smooth slide-in from right
- [ ] Belief vs. market price: side-by-side pill display
- [ ] Behavior trait bars with labels and values
- [ ] Evidence cards with sentiment color (green positive, red negative, amber mixed)
- [ ] Optional: mini sparkline of belief history

### F4.6 — Behavior Study View (Optional)
- [ ] Toggle panel showing all 9 agents' current beliefs vs. market price
- [ ] Scatter plot or horizontal bar chart
- [ ] Highlights disagreement regions
- [ ] Shows which agents are above/below market

## Acceptance Criteria
- [ ] Dashboard passes visual inspection as a prediction market UI
- [ ] No raw data dumps visible (all formatted)
- [ ] Chart looks clean and professional
- [ ] Agent drawer feels like a detailed inspector panel
