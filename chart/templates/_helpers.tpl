{{- define "kubeping.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end -}}

{{- define "kubeping.labels" -}}
app: {{ .Chart.Name }}
{{- end -}}

{{- define "kubeping.selectorLabels" -}}
app: {{ .Chart.Name }}
{{- end -}}

{{- define "kubeping.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- .Release.Name -}}-{{- .Chart.Name -}}
{{- else }}
{{- .Values.serviceAccount.name -}}
{{- end }}
{{- end -}}