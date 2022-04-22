#!/bin/bash

account="rafael.tinoco@canonical.com"
att="canonical"

echo """
/home/rafaeldtinoco/apps/gmail-oauth2-tools/python/oauth2.py --user=$account --client_id=$(secret-tool lookup $att client-id) --client_secret=$(secret-tool lookup $att client-secret) --refresh_token=$(secret-tool lookup $att refresh)
"""

exit 0

get_access_token() {
	{ IFS= read -r tokenline && IFS= read -r expireline; } < \
    <( \
    /home/rafaeldtinoco/apps/gmail-oauth2-tools/python/oauth2.py \
    --user="$account" \
	--client_id="$(secret-tool lookup $att client-id)" \
	--client_secret="$(secret-tool lookup $att client-secret)" \
	--refresh_token="$(secret-tool lookup $att refresh)")

	token=${tokenline#Access Token: }
	expire=${expireline#Access Token Expiration Seconds: }
}

token="$(secret-tool lookup $att token)"
expire="$(secret-tool lookup $att token-expire)"
now=$(date +%s)

if [[ $token && $expire && $now -lt $((expire - 60)) ]]; then
   echo $token
else
   get_access_token
   echo $token | secret-tool store --label=msmtp $att token
   expire=$((now + expire))
   echo $expire | secret-tool store --label=msmtp $att token-expire
   echo $token
fi
