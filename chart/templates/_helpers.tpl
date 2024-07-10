{{- define "probe-from-node.name" -}}
{{ .Chart.Name }}
{{- end -}}

{{- define "probe-from-node.fullname" -}}
{{ include "probe-from-node.name" . }}-{{ .Release.Name }}
{{- end -}}

{{- define "probe-from-node.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{ default (include "probe-from-node.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
{{ .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}

{{- define "probe-from-node.labels" -}}
app: {{ include "probe-from-node.name" . }}
{{- end -}}
