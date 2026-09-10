# Image-to-3D reconstruction models & how they are chosen

The skill is not hard-coded to one model. `i3dc/registry.py` is the single
source of truth and drives selection. It prefers, in order:

1. a **locally installed** image-to-3D model (whatever is present);
2. the **best lightweight local model** that fits the detected hardware;
3. **Blender-assisted** reconstruction (interactive fallback);
4. an **external service** — only when explicitly allowed in config.

Selection also folds in whether a model is installed. `--mesh <file>` skips
reconstruction entirely and uses a mesh you already have.

## Options that fit ~4 GB (RTX 2050)

| Model | Weights / peak need | Local on 4 GB? | Notes / install |
|---|---|---|---|
| **TripoSR** | ~1 / ~2 GB | Yes (fast) | `pip install git+https://github.com/VAST-AI-Research/TripoSR.git` |
| **Stable Fast 3D** (low) | ~2 / ~3.5 GB | Yes | `pip install git+https://github.com/Stability-AI/StableFast3D.git`; several memory configs |
| **Zero123plus** | ~3 / ~4.5 GB | Marginal → steer lighter | `pip install zero123plus` |
| **Trellis** | ~4 / ~6 GB | Too heavy on 4 GB → suggest lighter | MS high-quality, dense mesh |
| **Blender assisted** | 0 | Yes (manual/interactive) | No AI; import references + model by hand |

The registry marks CPU viability: a model that can run on CPU (slow) is still
offered when there is no GPU, with a speed warning. `install` fields are surfaced
to the user verbatim when a needed model is missing.

## Behaviour when nothing fits
`choose_recon()` returns either an installable lightweight recommendation (with
its `install` command) or an honest infeasible result. Executing a plan without
the model installed never produces a mesh — it returns `needs_mesh`/`skipped` and
tells you the install command.

## Never silent uploads
External image-to-3D services are only used when `allow_external_service: true`
AND a service is configured. Otherwise the skill explains that an external API
would be required and asks for explicit permission.
