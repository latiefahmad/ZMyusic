#!/usr/bin/env bash
# A release tag and the app's version stamp must agree. If they drift, the
# updater offers a version the downloaded APK does not call itself, so every
# launch offers the same update again. Run this from a tag job before
# anything is built.
set -euo pipefail

tag="${1:?usage: verify-release-tag.sh <tag>}"
version="${tag#ZMyusic-v}"

if [ "$version" = "$tag" ] || ! [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]]; then
  echo "::error::Tag '$tag' is not ZMyusic-v<major>.<minor>.<patch>."
  exit 1
fi

root="$(cd "$(dirname "$0")/../.." && pwd)"
gradle="$root/build.gradle.kts"
name="$(sed -n 's/^extra\["zmyusicVersionName"\] = "\(.*\)"/\1/p' "$gradle" | tr -d '\r')"
code="$(sed -n 's/^extra\["zmyusicVersionCode"\] = \([0-9]*\)/\1/p' "$gradle" | tr -d '\r')"
if [ -z "$name" ] || [ -z "$code" ]; then
  echo "::error::Could not read zmyusicVersionName / zmyusicVersionCode from build.gradle.kts."
  exit 1
fi
if [ "$version" != "$name" ]; then
  echo "::error::Tag $tag names $version, but zmyusicVersionName is $name. Bump the version (and zmyusicVersionCode) or use the right tag."
  exit 1
fi

# The Xcode project carries a second copy of the version. If it drifts, the
# IPA is built and named with the old number even though every Gradle build is
# correct.
pbx="$root/ios/App/ZMyusic.xcodeproj/project.pbxproj"
if [ -f "$pbx" ]; then
  ios_names="$(sed -n 's/^[[:space:]]*MARKETING_VERSION = \([^;]*\);/\1/p' "$pbx" | tr -d '\r' | sort -u)"
  ios_codes="$(sed -n 's/^[[:space:]]*CURRENT_PROJECT_VERSION = \([^;]*\);/\1/p' "$pbx" | tr -d '\r' | sort -u)"
  if [ "$ios_names" != "$name" ]; then
    echo "::error::iOS MARKETING_VERSION is '${ios_names:-<missing>}', but zmyusicVersionName is $name."
    exit 1
  fi
  if [ "$ios_codes" != "$code" ]; then
    echo "::error::iOS CURRENT_PROJECT_VERSION is '${ios_codes:-<missing>}', but zmyusicVersionCode is $code."
    exit 1
  fi
fi

# A published release is what /releases/latest serves the updater, so tagging
# an older version afterwards would move "latest" backwards. Re-running the
# same tag is allowed; going backwards is not.
if [ -n "${GH_TOKEN:-}" ] && [ -n "${GITHUB_REPOSITORY:-}" ]; then
  latest="$(gh api "repos/${GITHUB_REPOSITORY}/releases/latest" --jq .tag_name 2>/dev/null || true)"
  if [ -n "$latest" ] && [ "$latest" != "$tag" ]; then
    latest_version="${latest#ZMyusic-v}"
    latest_version="${latest_version#v}"
    core="${version%%-*}"
    latest_core="${latest_version%%-*}"
    if [ "$latest_core" != "$core" ]; then
      newest="$(printf '%s\n%s\n' "$latest_core" "$core" | sort -n -t. -k1,1 -k2,2 -k3,3 | tail -n1)"
      if [ "$newest" != "$core" ]; then
        echo "::error::Tag $tag is older than the latest published release $latest."
        exit 1
      fi
    fi
  fi
fi

echo "Tag $tag matches zmyusicVersionName $name (versionCode $code)."
