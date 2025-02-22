{{- define "object.name" -}}
{{ .Release.Name }}
{{- end -}}

{{- define "object.namespace" -}}
{{ .Release.Namespace }}
{{- end }}

{{- define "common.labels" -}}
app: {{ include "object.name" . }}
{{- if .Values.labels }}
{{- range $k, $v := .Values.labels }}
{{ $k }}: {{ $v }}
{{- end }}
{{- end }}
{{- end }}

{{- define "common.annotations" -}}
{{- if .Values.annotations }}
{{- range $k, $v := .Values.annotations }}
{{ $k }}: {{ $v }}
{{- end }}
{{- end }}
{{- end }}

{{- define "common.metadata" -}}
name: {{ include "object.name" . }}
namespace: {{ include "object.namespace" . }}
labels:
  {{ include "common.labels" . | nindent 2 }}
annotations:
  {{ include "common.annotations" . | nindent 2 }}
{{- end }}