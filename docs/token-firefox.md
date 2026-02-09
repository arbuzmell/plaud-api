# Getting Plaud Token — Firefox

## Step 1: Open Plaud web app

Go to [web.plaud.ai](https://web.plaud.ai) and sign in with your Google account.

## Step 2: Open Developer Tools

Use one of these methods:

| Method | Action |
|--------|--------|
| Keyboard (Mac) | `Cmd + Option + I` |
| Keyboard (Windows/Linux) | `F12` or `Ctrl + Shift + I` |
| Menu | `☰` → More Tools → Web Developer Tools |
| Right-click | Right-click anywhere → Inspect |

## Step 3: Go to the Network tab

Click the **Network** tab at the top of Developer Tools.

```
Inspector  Console  Debugger  ► Network ◄  Style Editor  ...
```

## Step 4: Trigger a request

Reload the page (`Cmd + R` / `Ctrl + R`) or navigate within the Plaud app. Requests will appear in the list.

## Step 5: Find any `api.plaud.ai` request

1. In the **filter field**, type `api.plaud`
2. Click on any request in the list

![Network tab — filter and select a request, then find Authorization header](images/devtools-network-tab.svg)

## Step 6: Copy the token

1. In the right panel, click the **Headers** tab
2. Scroll to **Request Headers**
3. Find the `Authorization` header:
   ```
   Authorization: bearer eyJhbGciOiJIUzI1NiIs...
   ```
4. Right-click the header → **Copy Value**

> **Copy everything after** `bearer ` — you only need the `eyJ...` part.


## Step 7: Save the token

```bash
plaud auth setup
```

Paste the token when prompted. It will be saved to `.env` in the current directory.

> **Note:** If you accidentally copied `bearer eyJ...`, that's fine — `plaud auth setup` strips the prefix automatically.

---

[← Back to README](../README.md)
