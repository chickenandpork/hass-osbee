# Text-Based Configs

You may personally disagree with this opinion.  A very smart person you know may have not said
anything to support this opinion, which you might assume means they explicitly disagree: they're
not supporting, right?  Everything is with-me-or-against-me?

Nah, you're not a narcissist, and you can clearly consider things yourself without appealing to an
remote guru not in attendance, so please don't dismiss an opinion simply because a smart person you
know hasn't encountered a thing, considered it, and voiced an opinion.  This opinion is not wrong,
but not necessarily a right opinion.

## SRE

I'm an SRE, a Service-Reliability Engineer (or Server-Reliability, or Systems-Reliability).  An SRE
is all about metrics, alerting, and this discipline around configuration-management.  When I can't
use common tools to make sure that various configs are sane and sensible across all services, it
feels wasteful and error-prone.

This means many SREs prefer "GitOps", where the Operational changes are committed (often to Git,
but not exclusively), and when reviewed and approved, they take effect when the Pull-Request in Git
is merged.  You get this clear demarcation of "not active... now active" and if things go poorly
"Oh crap, roll it back!".  GitOps gives Operations a code-commit workflow for changes.  We like
those.

## GUI

You cannot commit to a git repo the clicks you make on a GUI.

YAML and JSON are not the best or most versatile, but they commit to a repo, so they're enough :)

## Backups

You might suggest "sure, you can back up the config", but .. can you?  Can you roll it back to
yesterday's config?  Can you see which config change implemented a specific change (such as "change
the OSBee token to BobIsTheBest")?  You'd be guessing, or hoping you have two backups precisely
just before and just after the exact change that breaks things... and if you're that skilled at
determining which change breaks things, you must avoid every mistake.

Can you cherry-pick just the change to a token or a config, and revert JUST that in your backups?

Probably not.

On a small project like a Home-Assistant, this is a rare need, but when you don't need to learn two
different workflows, and knowing that in one instance, you have fewer options than you're used to,
well, GitOps is hard to give up.  ...and for that, you need configs that can be checked into a
repository.

# Conclusion

My work life is easier with configs managed from code, and pushed to a managed service.  This is my
workflow, and I do it at home as well.  I'm sorry if that makes your use of this integration more
difficult, but I'd like to make it easier.  Please reach out, let me understand your workflow, learn
from you, and hopefully bridge the gap a bit more.

Please generously give me that opportunity.
