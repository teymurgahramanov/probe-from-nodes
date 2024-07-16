{{- define "object.name" -}}
{{- $top := index . 0 -}}
{{- $itemName := index . 1 -}}
{{ .Release.Name }}
{{- end -}}

{{- define "object.namespace" -}}
{{- $Chart := .Chart -}}
{{ .Release.Namespace }}
{{- end }}

{{- define "common.labels" -}}
{{- $Chart := .Chart -}}
{{- if .Values.labels }}
{{- range $k, $v := .Values.labels }}
{{ $k }}: "{{ $v }}"
{{- end }}
{{- end }}
{{- end }}

{{- define "common.annotations" -}}
{{- $Chart := .Chart -}}
{{- if .Values.annotations }}
{{- range $k, $v := .Values.annotations }}
{{ $k }}: "{{ $v }}"
{{- end }}
{{- end }}
{{- end }}

{{- define "common.metadata" -}}
{{- $context := index . 0 -}}
{{- $args := index . 1 | default dict -}}
{{- $itemName := "" -}}
{{- $labelsPath := "" -}}
{{- $annotationsPath := "" -}}

{{- if hasKey $args "itemName" }}
  {{- $itemName = get $args "itemName" -}}
{{- else -}}
{{- end }}
{{- if hasKey $args "labelsPath" }}
  {{- $labelsPath = get $args "labelsPath" -}}
{{- end }}
{{- if hasKey $args "annotationsPath" }}
  {{- $annotationsPath = get $args "annotationsPath" -}}
{{- end }}

name: {{ include "object.name" (list $context $itemName) }}
namespace: {{ include "object.namespace" $context }}
labels:
  {{- if $labelsPath }}
  {{- $labels := $context.Values }}
  {{- range $key := splitList "." $labelsPath }}
  {{- $labels = index $labels $key | default dict }}
  {{- end }}
  {{- range $k, $v := $labels }}
  {{ $k }}: "{{ $v }}"
  {{- end }}
  {{- end }}
  {{ include "common.labels" $context | nindent 2 }}
annotations:
  {{- if $annotationsPath }}
  {{- $annotations := $context.Values }}
  {{- range $key := splitList "." $annotationsPath }}
  {{- $annotations = index $annotations $key | default dict }}
  {{- end }}
  {{- range $k, $v := $annotations }}
  {{ $k }}: "{{ $v }}"
  {{- end }}
  {{- end }}
  {{ include "common.annotations" $context | nindent 2 }}
{{- end }}