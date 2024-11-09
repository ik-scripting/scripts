#!/usr/bin/env bash

# https://edwin-philip.medium.com/argo-cd-app-diff-as-pr-comments-f58fe602ec79
#
String argoAppDiff(String app_name) {
  return sh(script: """#!/bin/bash -x +e
    argocd app diff ${app_name} --revision ${BRANCH}
  """, returnStdout: true).trim()
}

def PRComment () {
  if (env.CHANGE_ID) {
      def diff = argoAppDiff()
      def firstComment = true
      def diffComment = """## ${env.APP_NAME} argo app diff <!-- Comment #1 -->
```diff
No Changes found.
```"""
      int index = 0;
      while (index < diff.length()) {
          diffComment = """## ${env.APP_NAME} argo app diff <!-- Comment #${index+1} -->
```diff
${diff.substring(index, Math.min(index + 65000,diff.length()))}
```"""
          for (comment in pullRequest.comments) {
            if (comment.body.contains("${env.APP_NAME} argo app diff <!-- Comment #${index+1} -->")) {
                firstComment = false
                pullRequest.editComment(comment.id, diffComment)
            }
          }
          if (firstComment) {
              pullRequest.comment(diffComment)
          }
          index += 65000;
      }
      if (diff.length() == 0) {
          for (comment in pullRequest.comments) {
            if (comment.body.contains("${env.APP_NAME} argo app diff <!-- Comment #1 -->")) {
                firstComment = false
                pullRequest.editComment(comment.id, diffComment)
            }
          }
          if (firstComment) {
              pullRequest.comment(diffComment)
          }
      }
    }
  }
}
