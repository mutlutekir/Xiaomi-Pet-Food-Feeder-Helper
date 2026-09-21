# Xiaomi Pet Food Feeder Helper

A standalone Home Assistant integration that finds Xiaomi pet feeders
already set up through the official
[`ha_xiaomi_home`](https://github.com/XiaoMi/ha_xiaomi_home) integration and
adds a **"Feed now" button** for each one — right on the feeder's existing
device card — plus a generic `xiaomi_feeder_helper.call_action` service for
calling any other MIoT action by `siid`/`aiid`.

No manual `did`/`siid`/`aiid` typing needed for the button: add the
integration from the UI and it auto-detects your feeder.

## Why this exists

The official Xiaomi Home integration (and the community
[`hass-xiaomi-miot`](https://github.com/al-one/hass-xiaomi-miot)
alternative) does not create the entities needed to trigger a **manual /
instant feed** on the Xiaomi Smart Pet Feeder 2 (`xiaomi.feeder.iv2001`),
even though the device and the Mi Home app fully support it:

- [`ha_xiaomi_home` issue #1734](https://github.com/XiaoMi/ha_xiaomi_home/issues/1734) — "has no way to feed manually"
- [`hass-xiaomi-miot` issue #2073](https://github.com/al-one/hass-xiaomi-miot/issues/2073) — "most entities are missing"

The underlying capability already exists inside `ha_xiaomi_home`'s own code
(`MIoTClient`/`MIoTHttpClient.action_async`) — it's just never exposed as an
entity or service. This integration doesn't touch or modify any of
`ha_xiaomi_home`'s files (so it survives its updates); at setup/call time it
simply reaches into `hass.data["xiaomi_home"]["miot_clients"]`, where that
integration keeps its already-connected client objects, and calls the same
internal method its own buttons and switches use.

## Requirements

- The official [`ha_xiaomi_home`](https://github.com/XiaoMi/ha_xiaomi_home)
  integration must already be installed, configured, and your feeder added
  there — this integration does not replace it, it only reaches into its
  data.

## Installation

### HACS (custom repository)

1. HACS → the ⋮ menu (top right) → **Custom repositories**.
2. Add this repository's URL, category **Integration**.
3. Find "Xiaomi Feeder Helper" in HACS and install it.
4. Restart Home Assistant completely.

### Manual

1. Copy the `custom_components/xiaomi_feeder_helper` folder into your Home
   Assistant `config/custom_components/` folder (next to your existing
   `xiaomi_home` folder).
2. Restart Home Assistant completely.

You do **not** need to add anything to `configuration.yaml` — this is a
UI-configured integration (see below).

## Usage

### 1. Add the integration

**Settings → Devices & services → Add integration** → search for **"Xiaomi
Feeder Helper"**. It scans your already-configured `xiaomi_home` account(s)
for known feeder models; if it finds one (or more), it shows their name(s)
and a **Submit** button. Click it.

If it says no feeder was found, make sure `xiaomi_home` is set up and your
feeder is visible there first, then try adding the integration again.

### 2. Use the button

Open the feeder's device page (**Settings → Devices & services → Devices**,
find your feeder) — a new **"Feed now"** button entity is now listed there
alongside its other sensors/switches. Add it to your dashboard as a
**Button** card, or just press it from the device page.

### 3. (Optional) The generic action-call service

For any *other* missing MIoT action on any `xiaomi_home` device, you can
still call the generic service directly:

```yaml
service: xiaomi_feeder_helper.call_action
data:
  did: "YOUR_DEVICE_DID"
  siid: 2
  aiid: 1
  params:
    - 1
```

To find a device's `did`: open its page under **Settings → Devices &
services**, click the **⋮** menu → **Download diagnostics**, and look for
the `"did"` field in the downloaded JSON. To find `siid`/`aiid` for an
action, search the [MIoT-Spec-V2 database](https://home.miot-spec.com/) for
your device's model, or ask in the
[`ha_xiaomi_home` discussions](https://github.com/XiaoMi/ha_xiaomi_home/discussions).

## Supporting another feeder model

Only `xiaomi.feeder.iv2001` (Xiaomi Smart Pet Feeder 2) is included by
default. If you've confirmed the manual-feed `siid`/`aiid` for a different
Xiaomi feeder model, open an issue or a pull request adding its model string
to `FEEDER_MODELS` in
[`custom_components/xiaomi_feeder_helper/const.py`](custom_components/xiaomi_feeder_helper/const.py).

## How it works (technical)

- `ha_xiaomi_home` stores one `MIoTClient` object per configured account
  under `hass.data["xiaomi_home"]["miot_clients"]`, and each client exposes
  a `device_list` dict of the devices it manages (with `did` and `model`).
- The config flow / button platform scans those for known feeder models
  (`discovery.py`) and creates a `ButtonEntity` per match, attached to the
  **same** Home Assistant device `ha_xiaomi_home` already created for it
  (matching its `(xiaomi_home, "<cloud_server>_<did>")` device identifier),
  so the button shows up on the existing device card instead of a new one.
- Pressing the button (or calling the generic service) calls
  `miot_client.miot_http.action_async(did, siid, aiid, in_list=[...])` — the
  same cloud MIoT action-call endpoint `ha_xiaomi_home` itself uses
  internally for buttons/switches that *do* have entities.

Because discovery only reads `hass.data` at setup/call time (not at Home
Assistant startup), load order between this integration and `xiaomi_home`
doesn't matter, as long as `xiaomi_home` is set up by the time you add this
integration or press the button.

## Disclaimer

This project is not affiliated with, endorsed by, or supported by Xiaomi. It
does not include, bundle, or modify any of Xiaomi's own source code — it only
calls a public method on an already-running instance of the official
`ha_xiaomi_home` integration via Home Assistant's own runtime data store.
Use at your own risk.

## License

MIT — see [LICENSE](LICENSE).
