# DevOps Metrics

According to the research explains in the popular book Accelerate, there are four key metrics that high-performing DevOps organizations focus on:

- Lead time
- Deployment frequency
- Change fail rate
- Mean time to recovery (MTTR)

Those metrics are also frequently mentioned in [Puppet's yearly State Of DevOps Report](https://www.puppet.com/resources/state-of-devops-report) and Google's [DORA](https://dora.dev) research program.

Here I present a simple way how to measure the metric 'lead time' in CI/CD pipelines.

_Hint: while following instructions are for GCP Cloud Build pipelines, the same principle can also be applied to other pipeline frameworks._

## How it is working

The module [git-metrics](https://github.com/Praqma/git-metrics/) is mainly for creating statistic reports from code repositories but it's methods can also be leveraged in CD pipelines to examine commit metadata from annotated tags. This is achieved by adding a repository checkout and an additional final step to your deployment pipeline which utilizes git-metrics. The additional overhead is a reasonable trade-off in order to collect the insightful metrics mentioned before.
For lead time, it checks the commit's author date and simply calculates the time difference until time of deployment as measured by the CD pipeline.

## Usage

Build and push the docker image to the GCR: `docker build -t gcr.io/PROJECT_ID/devops-metrics . && docker push gcr.io/PROJECT_ID/devops-metrics`

Since Cloud Build is only doing a shallow checkout of a repository, you need to include a step to [fetch the entire history](https://cloud.google.com/build/docs/automating-builds/create-manage-triggers#including_the_repository_history_in_a_build) including tags:

```
  - name: gcr.io/cloud-builders/git
    dir: /workspace
    args:
      - fetch
      - '--unshallow'
      - '--tags'
      - 'git@github.com:${REPO_FULL_NAME}'
```

Insert a step like the following in your Cloud Build pipeline last step in order to measure two things: lead time and pipeline time. While the latter is not one of the four (since 2022 five) key metrics for DevOps success, it is a good proxy metric to track, since a very long running pipeline certainly contributes to less frequent deployments.

```
- name: 'gcr.io/my-images/devops-metrics'
  dir: /app
  env:
  - 'REPO_PATH=/workspace'
  - 'TAG_NAME=${TAG_NAME}'
  - 'BUILD_ID=${BUILD_ID}'
  - 'PROJECT_ID=${PROJECT_ID}'
```

## Graphing the metrics
The lead time will now be logged and can be extracted with a log-based metric of type distribution that uses following attributes:
- build filter: `resource.type="build" AND textPayload:"lead_time"`
- field name: `textPayload`
- regular expression: `lead_time:\s([0-9]+\.[0-9]{1,6})`
