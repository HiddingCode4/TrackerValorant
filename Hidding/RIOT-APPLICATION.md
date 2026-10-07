# Hidding — VALORANT companion prototype

## Product and current status

Hidding is an independent Windows companion intended for a public VALORANT audience. The current prototype runs locally and demonstrates a five-player teammate lobby, match-history analysis, a floating overlay, and an account-linking/consent flow. All lobby players, ranks, match results and consent states are synthetic. There is no live game integration, real Riot authentication or Riot approval.

The source repository being prepared is https://github.com/HiddingCode4/TrackerValorant. Contact details and a public presentation URL must be supplied by the project owner before submission. `PRESENTATION-RIOT.html` is a standalone, interactive review companion that can be opened locally without a server.

## Implemented prototype behavior

- Five fictional teammates, with statistics shown only for profiles whose simulated sharing state is enabled.
- A private profile with statistics hidden, an incomplete six-match history, a consistently strong profile and a profile with a recent ACS increase.
- Selection of a shared profile to inspect its recent match history and aggregate statistics.
- Desktop overlay opened/closed using Alt + W, without game-memory access or injection.
- A simulated account connection followed by a separate sharing choice. No credentials are requested.
- Withdrawal of simulated consent immediately hides the player's statistics in the lobby and overlay.
- Import of a normalized local JSON history, separate from the simulated lobby.
- Windows build scripts and a GitHub Actions build workflow.

## Requested integration

Production VALORANT API access and Riot Sign On. The planned match-history integration would use VAL-MATCH-V1 match lists by PUUID and match details by match ID, for authorized users. We would retrieve the most recent available matches and analyze up to ten matches in the chosen queue.

Live agent-select roster identification is a separate integration requirement. We are seeking guidance on an authorized data source and permitted overlay phases. This prototype does not claim the documented match-history API can identify a live lobby. Synthetic rank displays are illustrative; real rank availability and the completeness of available statistics must be verified during integration.

## Explicit feature-review request

We propose descriptive observations for consistently strong performance and recent changes in performance. A secondary account is one possible explanation among many. These observations cannot establish smurfing or cheating; they produce no cheating probability, alternate hidden MMR rating or automated report.

Current prototype thresholds are exploratory and unvalidated:

- Consistent dominance: at least six of ten matches have K/D >= 1.5 and ACS >= 280.
- Recent ACS increase: the average of the five newest matches is at least 40% higher than that of the five older matches.
- Fewer than ten available matches: insufficient history, with no profile conclusion.

We request explicit feedback on whether these observations are acceptable, including display phases and wording. We are prepared to modify or remove this feature in response to Riot's review. It is not presented as already approved.

## Planned consent and security

Production identity verification would redirect to Riot's official authentication page. Player data would be shown to other Hidding users only after explicit consent within Hidding. Deliberately hidden identities and non-consenting players would be respected. No opponent statistics would be displayed before the match.

A server over HTTPS would keep production API keys and RSO secrets out of the client executable and source repository, and enforce access controls, consent, rate limits, caching and withdrawal. Retention limits, deletion controls and complete production privacy/terms documents must be designed before launch.

## Prototype privacy

The desktop prototype makes no network requests. It asks for no Riot credentials. Local imported histories are loaded into memory and are not copied or persisted by the application. Simulated connection and sharing choices reset when the app closes. The HTML review companion similarly keeps its state only in page memory until reload. Build scripts download dependencies; GitHub Actions runs on GitHub infrastructure.

## Reviewer walkthrough

1. Launch `app.py` or open `PRESENTATION-RIOT.html`.
2. Inspect the five-player demo lobby: private profiles have no statistics.
3. Select Nova's shared profile and inspect the ten-match history supporting the dominance observation.
4. Inspect Echo's incomplete history and Lumen's five-match-group ACS comparison.
5. Preview the team overlay.
6. In Account & consent, simulate account connection. No password or real OAuth request occurs.
7. Explicitly enable sharing and confirm that Oreo's fictional lobby statistics become visible.
8. Withdraw consent and confirm that those statistics disappear.

## Remaining work

Real authentication, backend hosting, production privacy/terms, game/lobby integration, automatic retrieval, queue filtering, rank-aware calibration, distribution signing and Windows in-game testing. Approval and delivery dates are not assumed.

Hidding is not affiliated with, endorsed by or approved by Riot Games. VALORANT and Riot Games are trademarks of their respective owners.
