# Getting Plaud Token — Google Chrome

## Step 1: Open Plaud web app

Go to [web.plaud.ai](https://web.plaud.ai) and sign in with your Google account.

## Step 2: Open DevTools

Use one of these methods:

| Method | Action |
|--------|--------|
| Keyboard (Mac) | `Cmd + Option + I` |
| Keyboard (Windows/Linux) | `F12` or `Ctrl + Shift + I` |
| Menu | `⋮` → More Tools → Developer Tools |
| Right-click | Right-click anywhere → Inspect |

## Step 3: Go to the Network tab

Click the **Network** tab at the top of DevTools.

```
Elements  Console  Sources  ► Network ◄  Performance  ...
```

## Step 4: Trigger a request

Reload the page (`Cmd + R` / `Ctrl + R`) or navigate within the Plaud app (e.g. click on a recording). You'll see network requests appear in the list.

## Step 5: Find any `api.plaud.ai` request

1. In the **Filter** field, type `api.plaud.ai`
2. Click on any request in the list (e.g. `simple/web`, `list`, `filetag`)

![Network tab — filter and select a request, then find Authorization header](images/devtools-network-tab.svg)

## Step 6: Copy the token

1. In the right panel, click the **Headers** tab
2. Scroll down to **Request Headers**
3. Find the `Authorization` header — it looks like:
   ```
   Authorization: bearer eyJhbGciOiJIUzI1NiIs...
   ```
4. **Copy only the token** (everything after `bearer ` — without the word "bearer")

> **Tip:** Right-click the `Authorization` value → **Copy value**, then remove the `bearer ` prefix.


## Step 7: Save the token

```bash
plaud auth setup
```

Paste the token when prompted. It will be saved to `.env` in the current directory.

> **Note:** If you accidentally copied `bearer eyJ...`, that's fine — `plaud auth setup` strips the prefix automatically.

---

[← Back to README](../README.md)
