# Getting Plaud Token — Safari

## Step 0: Enable Developer Tools (one-time setup)

Safari has DevTools **disabled by default**. You need to turn them on first:

1. Open Safari → **Settings** (or `Cmd + ,`)
2. Go to the **Advanced** tab
3. Check **"Show features for web developers"**

![Safari Advanced Settings](images/safari-enable-devtools.svg)

After this, the **Develop** menu appears in the menu bar.

> On older macOS versions the checkbox may say **"Show Develop menu in menu bar"**.

## Step 1: Open Plaud web app

Go to [web.plaud.ai](https://web.plaud.ai) and sign in with your Google account.

## Step 2: Open Web Inspector

Use one of these methods:

| Method | Action |
|--------|--------|
| Keyboard | `Cmd + Option + I` |
| Menu | Develop → Show Web Inspector |
| Right-click | Right-click anywhere → Inspect Element |

## Step 3: Go to the Network tab

Click the **Network** tab at the top of Web Inspector.

```
Elements  Console  Sources  ► Network ◄  Timelines  ...
```

## Step 4: Trigger a request

Reload the page (`Cmd + R`) or navigate within the Plaud app. Requests will appear in the list.

## Step 5: Find any `api.plaud.ai` request

1. In the **filter field** (top-right), type `api.plaud`
2. Click on any request in the list

![Network tab — filter and select a request, then find Authorization header](images/devtools-network-tab.svg)

## Step 6: Copy the token

1. In the right panel, click **Headers**
2. Scroll to **Request Headers** section
3. Find the `Authorization` header:
   ```
   Authorization: bearer eyJhbGciOiJIUzI1NiIs...
   ```
4. Double-click the token value to select it, then `Cmd + C` to copy

> **Copy everything after** `bearer ` **(with a space)** — you only need the `eyJ...` part.


## Step 7: Save the token

```bash
plaud auth setup
```

Paste the token when prompted. It will be saved to `.env` in the current directory.

> **Note:** If you accidentally copied `bearer eyJ...`, that's fine — `plaud auth setup` strips the prefix automatically.

---

[← Back to README](../README.md)
