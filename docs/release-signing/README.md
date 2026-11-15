# Release signing trust

This directory contains the public SSH allowed-signers file used to verify
signed release tags. It contains public key material only. Never add a private
key, token, or credential here.

- Principal: `release@snaplyze.me`
- Key type: `ssh-ed25519`
- Used by: `git verify-tag` and the `Release` workflow's
  `RELEASE_TAG_ALLOWED_SIGNERS` trust source.

## Verify a tag

From a clone that contains this file:

```bash
git -c gpg.format=ssh \
  -c gpg.ssh.allowedSignersFile=docs/release-signing/allowed_signers \
  verify-tag vX.Y.Z
```

A signature from any other principal or key fails. The GitHub release workflow
reads the same file contents from `RELEASE_TAG_ALLOWED_SIGNERS` and is the
authoritative gate for publication.

## Rotation

1. Generate a new signing key and keep the private key outside this repository.
2. **Append** the new public line to `allowed_signers`; keep the old line for
   tags that are still supported and verified by tests.
3. Update the repository or environment variable `RELEASE_TAG_ALLOWED_SIGNERS`
   with the full file, including both keys during the transition.
4. Sign the next tag with the new key and verify it against this file.
5. Move the verification test to the new tag and confirm the old tag still
   verifies while its key remains in the file.
6. Remove the old public key only after no supported tag depends on it. Never
   replace the only key before the migration tag has passed verification.

Old tags remain verifiable only while their public key remains in the trust
file or in a separately retained copy. Record the rotation date and the reason
in the release issue or pull request.
