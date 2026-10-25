# Code as Primitives

Project blog template for Code as Primitives.

## Template source

The initial site was downloaded from [Schema Harness](https://schema-harness.github.io/)
using its [source repository](https://github.com/schema-harness/schema-harness.github.io)
at commit `537a5f245408b91bc98b3cb77ec42b4633e96dd6`.

`index.html` is preserved unchanged as the starting template, including the original
article, author attribution, figures, and interactive examples. Project-specific
content will be added separately. The upstream repository does not include a
license file; this repository does not assign a new license to the copied material.

## Files

- `index.html`: the complete static page, with embedded styles, scripts, and assets.
- `.nojekyll`: disables Jekyll processing for GitHub Pages.

No dependency installation or build step is required. Google Fonts is loaded
from Google's font service.

## Local preview

From this repository, run:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8000/>.

## GitHub Pages

Destination repository: <https://github.com/ZhiqiChen05/Code-as-Primitives>

Configure **Settings → Pages → Build and deployment** as follows:

- Source: **Deploy from a branch**
- Branch: **main**
- Folder: **/(root)**

Once GitHub Pages is enabled and the branch is pushed, the expected site URL is:
<https://ZhiqiChen05.github.io/Code-as-Primitives/>.

The `origin` remote points to the destination repository. The `template` remote
retains the original Schema Harness source. Future pushes to `main` publish the
static page after GitHub Pages is configured.
