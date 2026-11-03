# Chess-Tickle privacy policy - GitHub Pages copy

This repo publishes the privacy policy and landing page for **Chess-Tickle**
(`com.Ghostind.Chesstickle`, live on Google Play) as a GitHub Pages site.

## Why it is a separate repo, and why that matters

The app's own repo (`ghostplayer88/Chess-Tickle`) went **private on 2026-08-03**. Play
requires a publicly reachable privacy policy, so the policy lives here instead. **That
separation is load-bearing: it is why making the app repo private was safe.** Re-check it
before changing either repo's visibility.

## This is not the address in the Play Console

The Console's privacy-policy field holds **`https://chess-tickle.web.app/privacy.html`**,
served from the `chess-web` project on Firebase Hosting. This repo is the **older copy, and
it is still live** - the GitHub Pages address still resolves and still reads correctly.

So drift here never shows up as a broken link. Both pages load; they just quietly stop
saying the same thing. Two guards exist on the app side, both in `chess-app`:

- `PrivacyLinkTest.POLICY_URL` pins the in-app Settings button to the Console's address.
  **If the Console is ever pointed somewhere else, change that constant.**
- A second test fails if Settings points back at `ghostplayer88.github.io`. It once did,
  for a while, and nothing failed - because nothing was comparing the two.

**Keep the two copies in step on substance.** As of 2026-11-03 they agree: the same nine
sections, AdMob and ads disclosed, the 13+ age requirement, data deletion, and
`ghostpdev@gmail.com` as the support address. The markup differs (this copy is smaller and
older in style); the content must not.

## Working copies

This folder is a **stray gitlink** inside the `chess-app` tree (mode 160000, no
`.gitmodules`). It is not a real submodule - leave it unstaged in `chess-app`; staging it
only adds noise.

A second folder points at this same remote:
`../../chess-app-website.STALE-use-privacy_repo`. **This one is the real working copy.** Do
not push from the stale one; two copies sharing a remote is how one of them gets overwritten.

---

Machine-wide rules - commit/push/deploy, the PowerShell UTF-8 trap, no physical Android
device - are in `../../AGENTS.md`. The app's own rules are in `../AGENTS.md`.
