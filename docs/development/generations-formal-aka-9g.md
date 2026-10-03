# Document 1: TextProv Generational Marking, Formal Specification

## 1. Domain

- $B = \texttt{0xE0100}$
- $V = [B, B+\texttt{0xEF}]$ is the Variation Selectors Supplement (VS17–VS256), with $|V| = 240$.
- $\Sigma = \{0,\dots,15\}$ is the set of state indices.
- $\Sigma_0 = \{0,1,2,3,4\} \subset \Sigma$ is the set of defined states: 0 human, 1 ai, 2 mixed, 3 edited, 4 unknown. $\Sigma \setminus \Sigma_0$ is reserved.
- $\Gamma = \{0,\dots,9\}$ is the set of generations, in their usual order.
- $L = \Sigma \times \Gamma$ is the set of labels, with $|L| = 160$.
- $P$ i󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁e󠄁t󠄁 o󠄁f󠄁 P󠄁U󠄁A󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁s󠄁 l󠄁i󠄁s󠄁t󠄁e󠄁d󠄁 i󠄁n󠄁 t󠄁h󠄁e󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 (󠄁`mapping.json` `pua`)󠄁.󠄁 E󠄁a󠄁c󠄁h󠄁 $p \in P$ r󠄁e󠄁c󠄁o󠄁r󠄁d󠄁s󠄁 a󠄁 b󠄁a󠄁s󠄁e󠄁 c󠄁h󠄁a󠄁r󠄁a󠄁c󠄁t󠄁e󠄁r󠄁 $b(p)$ a󠄁n󠄁d󠄁 a󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 $s(p) \in \Sigma_0$.󠄁 I󠄁n󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 0󠄁.󠄁1󠄁,󠄁 $p = \texttt{0x100000} + b(p)$ a󠄁n󠄁d󠄁 $s(p) = 1$.󠄁

## 2. Encoding

**Def 2.1.** $\mathrm{enc}: L \to V,\quad \mathrm{enc}(s,g) = B + 16g + s$

**Def 2.2.** Let $D = [B, B+\texttt{0x9F}]$ (the default grid) and $R = [B+\texttt{0xA0}, B+\texttt{0xEF}]$ (reserved, $|R| = 80$).

$$\mathrm{dec}(c) = \begin{cases} \big((c-B) \bmod 16,\ \lfloor (c-B)/16 \rfloor\big) & c \in D \\ \bot_R & c \in R \end{cases}$$

**Prop 2.3 (Injectivity).** $\mathrm{enc}$ is injective and its image is exactly $D$.
*Proof.* Because $0 \le s < 16$, the value $16g + s$ is the two-digit base-16 number with digits $(g, s)$. Base-16 representations are unique. The largest value is $16\cdot 9 + 15 = \texttt{0x9F}$. ∎

**Prop 2.4.** $\mathrm{dec} \circ \mathrm{enc} = \mathrm{id}_L$.

$\bot_R$ i󠄁s󠄁 a󠄁 s󠄁i󠄁n󠄁g󠄁l󠄁e󠄁 v󠄁a󠄁l󠄁u󠄁e󠄁,󠄁 d󠄁i󠄁s󠄁t󠄁i󠄁n󠄁c󠄁t󠄁 f󠄁r󠄁o󠄁m󠄁 e󠄁v󠄁e󠄁r󠄁y󠄁 l󠄁a󠄁b󠄁e󠄁l󠄁 i󠄁n󠄁 $L$ a󠄁n󠄁d󠄁 f󠄁r󠄁o󠄁m󠄁 t󠄁h󠄁e󠄁 a󠄁b󠄁s󠄁e󠄁n󠄁c󠄁e󠄁 o󠄁f󠄁 a󠄁 m󠄁a󠄁r󠄁k󠄁.󠄁 I󠄁t󠄁 i󠄁s󠄁 w󠄀h󠄀a󠄀t󠄀 a󠄀 d󠄀e󠄀c󠄀o󠄀d󠄀e󠄀r󠄀 r󠄀e󠄀p󠄀o󠄀r󠄀t󠄀s󠄀 f󠄀o󠄀r󠄀 a󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁 i󠄁n󠄁 $R$ w󠄁h󠄁o󠄁s󠄁e󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 (󠄁D󠄁e󠄁f󠄁 2󠄁.󠄁7󠄁)󠄁 i󠄁t󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁.󠄁

**P󠄀r󠄀o󠄀p󠄀 2󠄀.󠄀5󠄀 (󠄀C󠄀o󠄀n󠄀t󠄀e󠄀x󠄀t󠄀-󠄀f󠄀r󠄀e󠄀e󠄀d󠄀o󠄀m󠄀)󠄀.󠄀** $\mathrm{dec}(c)$ d󠄀e󠄀p󠄀e󠄀n󠄀d󠄀s󠄀 o󠄀n󠄀l󠄀y󠄀 o󠄀n󠄀 $c$.󠄀 N󠄀o󠄀 h󠄀e󠄀a󠄀d󠄀e󠄀r󠄀,󠄀 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 declaration or neighbouring character is needed to decode it.

**Prop 2.6 (Backward compatibility).** For $s \in \Sigma_0$, $\mathrm{enc}(s,0) = B + s$. These are the current spec's U+E0100–U+E0104.

**D󠄁e󠄁f󠄁 2󠄁.󠄁7󠄁 (󠄁S󠄁t󠄁r󠄁i󠄁d󠄁e󠄁)󠄁.󠄁** A󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 i󠄁s󠄁 a󠄁n󠄁 e󠄁n󠄁c󠄁o󠄁d󠄁i󠄁n󠄁g󠄁 o󠄁t󠄁h󠄁e󠄁r󠄁 t󠄁h󠄁a󠄁n󠄁 D󠄁e󠄁f󠄁 2󠄁.󠄁1󠄁 t󠄁h󠄁a󠄁t󠄁 o󠄁c󠄁c󠄁u󠄁p󠄁i󠄁e󠄁s󠄁 a󠄁 s󠄁u󠄁b󠄁-󠄁r󠄁a󠄁n󠄁g󠄁e󠄁 o󠄁f󠄁 $R$,󠄁 f󠄁o󠄁r󠄁 e󠄁x󠄁a󠄁m󠄁p󠄁l󠄁e󠄁 o󠄁n󠄁e󠄁 w󠄁i󠄁t󠄁h󠄁 f󠄁e󠄁w󠄁e󠄁r󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁 p󠄁e󠄁r󠄁 r󠄁o󠄁w󠄁 a󠄁n󠄁d󠄁 m󠄁o󠄁r󠄁e󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁s󠄁.󠄁 T󠄁h󠄁e󠄁 d󠄁e󠄁f󠄁a󠄁u󠄁l󠄁t󠄁 g󠄁r󠄁i󠄁d󠄁 i󠄁s󠄁 n󠄁o󠄁t󠄁 a󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁.󠄁 A󠄁 p󠄀r󠄀o󠄀d󠄀u󠄀c󠄀e󠄀r󠄀 e󠄀i󠄀t󠄀h󠄀e󠄀r󠄀 i󠄀m󠄀p󠄀l󠄀e󠄀m󠄀e󠄀n󠄀t󠄀s󠄀 a󠄀 s󠄀t󠄀r󠄀i󠄀d󠄀e󠄀 o󠄀r󠄀 p󠄀a󠄀s󠄀s󠄀e󠄀s󠄀 i󠄀t󠄀 t󠄁h󠄁r󠄁o󠄁u󠄁g󠄁h󠄁 (󠄁C󠄁5󠄁)󠄁.󠄁

**D󠄁e󠄁f󠄁 2󠄁.󠄁8󠄁 (󠄁P󠄁U󠄁A󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁i󠄁n󠄁g󠄁)󠄁.󠄁** $\delta: P \to \mathbb{U} \times V,\quad \delta(p) = \big(b(p),\ \mathrm{enc}(s(p), 0)\big)$,󠄁 w󠄁h󠄁e󠄁r󠄁e󠄁 $\mathbb{U}$ i󠄁s󠄁 t󠄁h󠄁e󠄁 s󠄁e󠄁t󠄁 o󠄁f󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁s󠄁.󠄁 A󠄁 P󠄁U󠄁A󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁s󠄁 t󠄁o󠄁 i󠄁t󠄁s󠄁 b󠄁a󠄁s󠄁e󠄁 c󠄁h󠄁a󠄁r󠄁a󠄁c󠄁t󠄁e󠄁r󠄁 f󠄁o󠄁l󠄁l󠄁o󠄁w󠄁e󠄁d󠄁 b󠄁y󠄁 t󠄁h󠄁e󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁 f󠄁o󠄁r󠄁 i󠄁t󠄁s󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁 a󠄁t󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 0󠄁,󠄁 a󠄁s󠄁 i󠄁n󠄁 A󠄁D󠄁R󠄁 0󠄁0󠄁0󠄁3󠄁.󠄁 P󠄁U󠄁A󠄁 h󠄁a󠄁s󠄁 n󠄁o󠄁 f󠄁o󠄁r󠄁m󠄁 f󠄁o󠄁r󠄁 $g > 0$.󠄁

## 3. Operations

**Def 3.1 (Saturating successor).** $\sigma: \Gamma \to \Gamma,\quad \sigma(g) = \min(g+1, 9)$

**Def 3.2 (Author).** For $s \in \Sigma_0$, $\alpha_s$ emits $\mathrm{enc}(s, 0)$.

**Def 3.3 (󠄁R󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁e󠄁)󠄁.󠄁** $\rho: L \to L,\quad \rho(s,g) = (s, \sigma(g))$

**Def 3.4 (󠄁R󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁e󠄁 on code points).**

$$\hat\rho(c) = \begin{cases} c + 16 & c \le B+\texttt{0x8F} \\ c & B+\texttt{0x90} \le c \le B+\texttt{0x9F} \\ c & c \in R \text{ (pass-through)} \end{cases}$$

On $D$, $\hat\rho = \mathrm{enc} \circ \rho \circ \mathrm{dec}$.

**D󠄁e󠄁f󠄁 3󠄁.󠄁5󠄁 (󠄁R󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁e󠄁 o󠄁n󠄁 P󠄁U󠄁A󠄁)󠄁.󠄁** R󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁e󠄁 f󠄁i󠄁r󠄁s󠄁t󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁s󠄁,󠄁 t󠄁h󠄁e󠄁n󠄁 i󠄁n󠄁c󠄁r󠄁e󠄁m󠄁e󠄁n󠄁t󠄁s󠄁.󠄁 F󠄁o󠄁r󠄁 $p \in P$ w󠄁i󠄁t󠄁h󠄁 $\delta(p) = (b, c)$,󠄁

$$\hat\rho(p) = \big(b,\ \hat\rho(c)\big)$$

I󠄁n󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁r󠄁y󠄁 0󠄁.󠄁1󠄁 t󠄁h󠄁i󠄁s󠄁 i󠄁s󠄁 $b(p)$ f󠄁o󠄁l󠄁l󠄁o󠄁w󠄁e󠄁d󠄁 b󠄁y󠄁 $\mathrm{enc}(1, 1)$.󠄁 T󠄁h󠄁e󠄁 o󠄁u󠄁t󠄁p󠄁u󠄁t󠄁 o󠄁f󠄁 r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁e󠄁 c󠄁o󠄁n󠄁t󠄁a󠄁i󠄁n󠄁s󠄁 n󠄁o󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁 o󠄁f󠄁 $P$.󠄁

## 4. Properties

| # | Property | Statement |
|---|---|---|
| P1 | S󠄁t󠄁a󠄁t󠄁e󠄁 invariance | $\pi_\Sigma(\rho(\ell)) = \pi_\Sigma(\ell)$ |
| P2 | Inflationary, monotone | $g \le \sigma(g)$; $g \le g' \Rightarrow \sigma(g) \le \sigma(g')$ |
| P3 | Iteration | $\rho^n(s,g) = (s, \min(g+n, 9))$ |
| P4 | Fixed points | $\rho(\ell) = \ell \iff \ell \in \Sigma \times \{9\}$ |
| P5 | Monoid structure | $\{\rho^n : n \in \mathbb{N}\} = \{\rho^0,\dots,\rho^9\} \cong (\Gamma, \oplus)$, where $a \oplus b = \min(a+b, 9)$ |
| P6 | Information loss | $\rho$ is injective on $\Sigma \times \{0..8\}$, but $\rho(s,8) = \rho(s,9)$ |
| P7 | Semantics-agnostic | $\hat\rho$ preserves $s$ for every $s \in \Sigma$, including reserved states |
| P8 | Closure | $\hat\rho(D) \subseteq D$ and $\hat\rho(R) = R$ |
| P9 | Mark-count invariance | $\hat\rho$ replaces one selector with one s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁.󠄁 O󠄁n󠄁 $P$ (󠄁D󠄁e󠄁f󠄁 3󠄁.󠄁5󠄁)󠄁 o󠄁n󠄁e󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁 b󠄁e󠄁c󠄁o󠄁m󠄁e󠄁s󠄁 t󠄁w󠄁o󠄁;󠄁 t󠄁h󠄁e󠄁 n󠄁u󠄁m󠄁b󠄁e󠄁r󠄁 o󠄁f󠄁 m󠄁a󠄁r󠄁k󠄁e󠄁d󠄁 c󠄁l󠄁u󠄁s󠄁t󠄁e󠄁r󠄁s󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁 |

**Corollary 4.1 (Observational semantics).** Assume conforming producers. If $\mathrm{dec}(c) = (s,g)$ with $g < 9$, the true hop count is exactly $g$. If $g = 9$, the true hop count is at least 9.

**Corollary 4.2 (Forward compatibility).** By P7, a regurgitator that follows this version also increments states defined in later versions correctly, without knowing what those states mean.

**Corollary 4.3 (Composition).** By P5, the effect of several regurgitate chains combines by saturating addition of their hop counts.

## 5. Conformance

- **C1.** Each grapheme cluster carries at most one selector from $V$. This rule is inherited from the spec.
- **C2.** An author operation emits $g = 0$ only. A󠄁n󠄁 a󠄁u󠄁t󠄁h󠄁o󠄁r󠄁 m󠄁a󠄁y󠄁 u󠄁s󠄁e󠄁 a󠄁n󠄁y󠄁 s󠄁u󠄁b󠄁s󠄁e󠄁t󠄁 o󠄁f󠄁 $\Sigma_0$.󠄁
- **C󠄁3󠄁.󠄁** R󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁e󠄁 (󠄀$\hat\rho$)󠄀 i󠄀s󠄀 a󠄀p󠄀p󠄀l󠄀i󠄀e󠄀d󠄀 e󠄀x󠄀a󠄀c󠄀t󠄀l󠄀y󠄀 o󠄀n󠄀c󠄀e󠄀 p󠄀e󠄀r󠄀 c󠄀l󠄀u󠄀s󠄀t󠄀e󠄀r󠄀 e󠄀a󠄀c󠄀h󠄀 t󠄀i󠄀m󠄀e󠄀 m󠄀a󠄀r󠄀k󠄀e󠄀d󠄀 t󠄀e󠄀x󠄀t󠄀 m󠄀o󠄀v󠄀e󠄀s󠄀 f󠄀r󠄀o󠄀m󠄀 a󠄀 t󠄀r󠄀a󠄀n󠄀s󠄀c󠄀r󠄀i󠄀p󠄀t󠄀 i󠄀n󠄀t󠄀o󠄀 t󠄀h󠄀e󠄀 i󠄀n󠄀p󠄀u󠄀t󠄀 o󠄀f󠄀 a󠄀 n󠄀e󠄀w󠄀 c󠄀o󠄀n󠄀v󠄀e󠄀r󠄀s󠄀a󠄀t󠄀i󠄀o󠄀n󠄀.󠄀 A󠄁 r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁o󠄁r󠄁 M󠄁U󠄁S󠄁T󠄁 a󠄁p󠄁p󠄁l󠄁y󠄁 i󠄁t󠄁 t󠄁o󠄁 e󠄁v󠄁e󠄁r󠄁y󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁 i󠄁n󠄁 $D$,󠄁 i󠄁n󠄁c󠄁l󠄁u󠄁d󠄁i󠄁n󠄁g󠄁 s󠄁t󠄁a󠄁t󠄁e󠄁s󠄁 i󠄁t󠄁 d󠄁o󠄁e󠄁s󠄁 n󠄁o󠄁t󠄁 k󠄁n󠄁o󠄁w󠄁 (󠄁P󠄁7󠄁)󠄁,󠄁 a󠄁n󠄁d󠄁 M󠄁U󠄁S󠄁T󠄁 N󠄁O󠄁T󠄁 s󠄁a󠄁t󠄁u󠄁r󠄁a󠄁t󠄁e󠄁 b󠄁e󠄁l󠄁o󠄁w󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 9󠄁.󠄁 C󠄁o󠄁r󠄁o󠄁l󠄁l󠄁a󠄁r󠄁y󠄁 4󠄁.󠄁1󠄁 d󠄁e󠄁p󠄁e󠄁n󠄁d󠄁s󠄁 o󠄁n󠄁 t󠄁h󠄁i󠄁s󠄁.󠄁 A󠄁 c󠄁o󠄁a󠄁r󠄁s󠄁e󠄁r󠄁 s󠄁c󠄁a󠄁l󠄁e󠄁 i󠄁s󠄁 a󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 (󠄁C󠄁6󠄁)󠄁,󠄁 n󠄁o󠄁t󠄁 a󠄀 s󠄀u󠄀b󠄀s󠄀e󠄀t󠄀 o󠄀f󠄀 t󠄀h󠄀e󠄀 d󠄀e󠄀f󠄀a󠄀u󠄀l󠄀t󠄀 g󠄁r󠄁i󠄁d󠄁.󠄁
- **C󠄁4󠄁.󠄁** R󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁e󠄁 i󠄀s󠄀 a󠄀 s󠄀e󠄀p󠄀a󠄀r󠄀a󠄀t󠄀e󠄀 o󠄀p󠄀e󠄀r󠄀a󠄀t󠄀i󠄀o󠄀n󠄀 f󠄀r󠄀o󠄀m󠄀 m󠄀a󠄀r󠄀k󠄀i󠄀n󠄀g󠄀.󠄀 T󠄀h󠄀e󠄀 s󠄀p󠄀e󠄀c󠄀'󠄀s󠄀 n󠄀o󠄀n󠄀-󠄀o󠄀v󠄀e󠄀r󠄀w󠄀r󠄀i󠄀t󠄀e󠄀 r󠄀u󠄀l󠄀e󠄀 g󠄀o󠄀v󠄀e󠄀r󠄀n󠄀s󠄀 $s$.󠄀 R󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁e󠄁 c󠄀h󠄀a󠄀n󠄀g󠄀e󠄀s󠄀 o󠄀n󠄀l󠄀y󠄀 $g$ a󠄀n󠄀d󠄀 M󠄀U󠄀S󠄀T󠄀 N󠄀O󠄀T󠄀 c󠄀h󠄀a󠄀n󠄀g󠄀e󠄀 $s$.󠄀
- **C󠄀5󠄀.󠄀** A󠄀 p󠄀r󠄀o󠄀d󠄀u󠄀c󠄀e󠄀r󠄀 e󠄀i󠄀t󠄀h󠄀e󠄀r󠄀 i󠄀m󠄀p󠄀l󠄀e󠄀m󠄀e󠄀n󠄀t󠄀s󠄀 a󠄀 s󠄀t󠄀r󠄀i󠄀d󠄀e󠄀 o󠄀r󠄀 p󠄀a󠄀s󠄀s󠄀e󠄀s󠄀 i󠄀t󠄀 t󠄁h󠄁r󠄁o󠄁u󠄁g󠄁h󠄁:󠄁 i󠄁t󠄁 M󠄁U󠄁S󠄁T󠄁 l󠄁e󠄁a󠄁v󠄁e󠄁 u󠄁n󠄁c󠄁h󠄁a󠄁n󠄁g󠄁e󠄁d󠄁 e󠄁v󠄁e󠄁r󠄁y󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁 i󠄁n󠄁 $R$ t󠄁h󠄁a󠄁t󠄁 b󠄁e󠄁l󠄁o󠄁n󠄁g󠄁s󠄁 t󠄁o󠄁 a󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 i󠄁t󠄁 d󠄁o󠄁e󠄁s󠄁n󠄁'󠄁t󠄁 i󠄁m󠄁p󠄁l󠄁e󠄁m󠄁e󠄁n󠄁t󠄁,󠄁 o󠄁r󠄁 t󠄁o󠄁 n󠄁o󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 i󠄁t󠄁 k󠄁n󠄁o󠄁w󠄁s󠄁.󠄁
- **C󠄁6󠄁.󠄁** A󠄁 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁 M󠄀U󠄀S󠄀T󠄀 o󠄀c󠄀c󠄀u󠄀p󠄀y󠄀 a󠄀 s󠄀u󠄀b󠄀-󠄀r󠄀a󠄀n󠄀g󠄀e󠄀 o󠄀f󠄀 $R$ t󠄀h󠄀a󠄀t󠄀 d󠄀o󠄀e󠄀s󠄀n󠄀'󠄀t󠄀 o󠄀v󠄀e󠄀r󠄀l󠄀a󠄀p󠄀 $D$ o󠄀r󠄀 a󠄀n󠄀y󠄀 o󠄀t󠄀h󠄀e󠄀r󠄀 s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁.󠄁 T󠄀h󠄀i󠄀s󠄀 k󠄀e󠄀e󠄀p󠄀s󠄀 P󠄀r󠄀o󠄀p󠄀 2󠄀.󠄀5󠄀 t󠄀r󠄀u󠄀e󠄀.󠄀
- **C󠄁7󠄁.󠄁** P󠄁U󠄁A󠄁 i󠄁s󠄁 g󠄁e󠄁n󠄁e󠄁r󠄁a󠄁t󠄁i󠄁o󠄁n󠄁 0󠄁 o󠄁n󠄁l󠄁y󠄁.󠄁 A󠄁 r󠄁e󠄁g󠄁u󠄁r󠄁g󠄁i󠄁t󠄁a󠄁t󠄁o󠄁r󠄁 t󠄁h󠄁a󠄁t󠄁 m󠄁e󠄁e󠄁t󠄁s󠄁 a󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁 i󠄁n󠄁 $P$ M󠄁U󠄁S󠄁T󠄁 d󠄁e󠄁c󠄁o󠄁d󠄁e󠄁 i󠄁t󠄁 t󠄁o󠄁 b󠄁a󠄁s󠄁e󠄁 p󠄁l󠄁u󠄁s󠄁 s󠄁e󠄁l󠄁e󠄁c󠄁t󠄁o󠄁r󠄁 (󠄁D󠄁e󠄁f󠄁 2󠄁.󠄁8󠄁)󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁n󠄁 i󠄁n󠄁c󠄁r󠄁e󠄁m󠄁e󠄁n󠄁t󠄁 (󠄁D󠄁e󠄁f󠄁 3󠄁.󠄁5󠄁)󠄁.󠄁 I󠄁t󠄁 M󠄁U󠄁S󠄁T󠄁 N󠄁O󠄁T󠄁 l󠄁e󠄁a󠄁v󠄁e󠄁 t󠄁h󠄁e󠄁 P󠄁U󠄁A󠄁 c󠄁o󠄁d󠄁e󠄁 p󠄁o󠄁i󠄁n󠄁t󠄁 i󠄁n󠄁 p󠄁l󠄁a󠄁c󠄁e󠄁.󠄁

## 6. Open (not settled by this document)

- **O1. Edit.** How a regurgitated cluster is labelled after it is modified: $(3, 0)$, $(s, g)$ kept, or something else.
- **O2. Join.** How $s$ is computed when labels combine into `mixed`, and what $g$ the result gets ($\max$, $\min$, or $0$).
- **O3. Unmarked input.** Whether regurgitate leaves unmarked clusters unmarked or assigns $(4, 1)$.
- **O4. Allocation within $R$.** How s󠄁t󠄁r󠄁i󠄁d󠄁e󠄁s󠄁 a󠄁r󠄁e󠄁 r󠄁e󠄁g󠄁i󠄁s󠄁t󠄁e󠄁r󠄁e󠄁d󠄁 a󠄁n󠄁d󠄁 i󠄁d󠄁e󠄁n󠄁t󠄁i󠄁f󠄁i󠄁e󠄁d󠄁.󠄁

T󠄁h󠄁i󠄁s󠄁 d󠄁o󠄁c󠄁u󠄁m󠄁e󠄁n󠄁t󠄁 s󠄀t󠄀o󠄀p󠄀s󠄀 a󠄀t󠄀 t󠄀h󠄀e󠄀 c󠄀o󠄀d󠄀e󠄀 p󠄀o󠄀i󠄀n󠄀t󠄀.󠄀 W󠄁h󠄁e󠄁t󠄁h󠄁e󠄁r󠄁 r󠄀u󠄀n󠄀s󠄀 m󠄀e󠄀r󠄀g󠄀e󠄀 a󠄀c󠄀r󠄀o󠄀s󠄀s󠄀 g󠄀e󠄀n󠄀e󠄀r󠄀a󠄀t󠄀i󠄀o󠄀n󠄀s󠄀,󠄀 w󠄀h󠄀a󠄀t󠄀 `merge_whitespace` d󠄁o󠄁e󠄁s󠄁,󠄁 t󠄁h󠄁e󠄁 m󠄁a󠄁r󠄁k󠄁u󠄁p󠄁 a󠄁t󠄁t󠄁r󠄁i󠄁b󠄁u󠄁t󠄁e󠄁 a󠄁n󠄁d󠄁 t󠄁h󠄁e󠄁 f󠄁i󠄁x󠄁t󠄁u󠄁r󠄁e󠄁 f󠄁o󠄁r󠄁m󠄁a󠄁t󠄁 b󠄁e󠄁l󠄁o󠄁n󠄁g󠄁 t󠄁o󠄁 t󠄁h󠄁e󠄁 A󠄁P󠄁I󠄁 l󠄁a󠄁y󠄁e󠄁r󠄁.󠄁 T󠄁h󠄁e󠄁y󠄁 a󠄁r󠄁e󠄁 o󠄁p󠄁e󠄁n󠄁 q󠄁u󠄁e󠄁s󠄁t󠄁i󠄁o󠄁n󠄁 8󠄁 i󠄁n󠄁 t󠄁h󠄁e󠄁 s󠄁p󠄁e󠄁c󠄁i󠄁f󠄁i󠄁c󠄁a󠄁t󠄁i󠄁o󠄁n󠄁.󠄁
