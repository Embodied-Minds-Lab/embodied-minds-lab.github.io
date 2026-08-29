## Getting started

1. Request a FASRC account ([quickstart guide](https://docs.rc.fas.harvard.edu/kb/quickstart-guide/)) under the **ydu_lab** group and set up OpenAuth two-factor.
2. Log in with `ssh <username>@login.rc.fas.harvard.edu`.
3. Skim the [Kempner handbook](https://handbook.eng.kempnerinstitute.harvard.edu) for cluster details.

## Cluster rules

1. **Never compute on login nodes.** Use `salloc` for interactive work, `sbatch` for jobs.
2. **Always use the `kempner_requeue` or `gpu_requeue` Slurm partitions** for background and interactive GPU jobs. Checkpoint everything. Requeue jobs get preempted and must resume on their own.
3. **Alternatively, use the `kempner_interactive` or `gpu_test` Slurm partitions for interactive jobs.** These provide MIG-partitioned A100 GPUs with 20 GB of memory each, and jobs have a maximum duration of 12 hours.
4. **The `kempner_h100`, `kempner_h200`, and `seas_gpu` Slurm partitions need Yilun's approval** — ask him first.
5. **Watch your storage** continuously, and clean up what you no longer need.

## Fairshare

Every lab has a fairshare score that sets our job priority: the more compute we burn, the lower it drops. Requeue partitions charge about **half** the fairshare because jobs there can be preempted. Around conference deadlines the cluster is heavily contended, so the score we conserve the rest of the year is what gets our jobs scheduled ahead of other labs'.

Check it with `sshare --account=ydu_lab -a`.

## Storage

| Path | Use it for | Notes |
| --- | --- | --- |
| `$HOME` | code and configs | 100 GB, backed up |
| `/n/lab_storage/ydu_lab` | code and small essential datasets | 100 TB, shared across the lab |
| `/n/netscratch/ydu_lab` | large datasets, results, wandb logs, intensive I/O | 50 TB, fast, **deleted after 90 days** |

Keep heavy I/O on netscratch. Running it against `$HOME` or lab storage slows the cluster for everyone.

Netscratch deletion is based on modification time, so `touch` will reset the clock on a file you still need. Use this **sparingly**: the space is shared, and anything parked there indefinitely is space the rest of the lab cannot use.

To store a large dataset permanently, contact Yilun. If the dataset is important and likely useful to many labs, he can approve you to request that Kempner host it in their testbed at `/n/holylfs06/LABS/kempner_shared/Everyone/testbed`, which is shared across the Kempner community.

If you need a large dataset for only a short time, talk to Yilun about acquiring temporary netscratch storage.

## Lab dashboard

The [lab dashboard](https://embodied-minds-lab.github.io/labdash-site/) shows our storage and compute usage at a glance. Please monitor it periodically so you can see when you are using more storage or compute than the average and reduce your usage.

## Slurm commands

A batch job on requeue, resuming from its last checkpoint:

```bash
#!/bin/bash
#SBATCH --job-name=my_job
#SBATCH --account=ydu_lab
#SBATCH --partition=kempner_requeue
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=1-00:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --requeue

python train.py --resume-from-checkpoint latest
```

An interactive session:

```bash
salloc --account=ydu_lab --partition=kempner_requeue --gres=gpu:1 --mem=64G --time=04:00:00
```

Day to day:

```bash
squeue -u $USER     # your jobs
scancel <jobid>     # kill a job
sacct -j <jobid>    # what happened to a job
```

## Resources

- [Lab dashboard](https://embodied-minds-lab.github.io/labdash-site/): storage and compute usage
- [Lab wiki](https://github.com/harvard-embodied-intelligence/lab-wiki): setup, environments, and workflows in depth
- [Lab GitHub](https://github.com/Embodied-Minds-Lab)
- [Yilun Du](https://yilundu.github.io/)
- [FASRC docs](https://docs.rc.fas.harvard.edu/): accounts, storage, and running jobs
- [Kempner handbook](https://handbook.eng.kempnerinstitute.harvard.edu): cluster and partition details
