# Changelog

## Unreleased

### Changes

* **Merged python-tldap library**: The python-tldap library (previously maintained as a separate repository at https://github.com/Karaage-Cluster/python-tldap) has been merged into the main Karaage repository. The `tldap` package is now included directly in Karaage and no longer needs to be installed as a separate dependency. This simplifies installation and dependency management.

## [6.3.1](https://github.com/Karaage-Cluster/karaage/compare/v6.3.0...v6.3.1) (2025-03-27)


### Bug Fixes

* update email templates ([#1549](https://github.com/Karaage-Cluster/karaage/issues/1549)) ([6bccdf3](https://github.com/Karaage-Cluster/karaage/commit/6bccdf326183dcc630527815f1ee950fb3b7e1e4))

## 6.3.0 (2025-03-01)


### Features

* Add PROJECT_DEACTIVE_AFTER_EXPIRATION setting ([2b1b064](https://github.com/Karaage-Cluster/karaage/commit/2b1b0640e79e8b7a7d48accc8222f3bf267c3245))


### Bug Fixes

* Remove duplicate / in project renewal email url ([a9f42da](https://github.com/Karaage-Cluster/karaage/commit/a9f42dae4f5ec773bf5de21a185cee2f3544d4e1))
* rename setting to PROJECT_DEACTIVATE_AFTER_EXPIRATION ([3575499](https://github.com/Karaage-Cluster/karaage/commit/3575499edeecae8ad5c6db559cb3adc98749c20d))
* upgrade slurm to 24.05 ([c552b9a](https://github.com/Karaage-Cluster/karaage/commit/c552b9aa167d0c5d5477a4a3e73c8d8abf818b3a))
* use Ubuntu 22.04 for tests ([49100ba](https://github.com/Karaage-Cluster/karaage/commit/49100ba1b592d2d230d5783b176835745f26b3d0))


### Miscellaneous Chores

* release 6.3.0 ([bf4b2fb](https://github.com/Karaage-Cluster/karaage/commit/bf4b2fb6caf50b52ef8e40030a53ffad57029f33))
