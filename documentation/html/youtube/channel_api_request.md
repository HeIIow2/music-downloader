# Results

## Request

```curl
curl 'https://www.youtube.com/youtubei/v1/browse?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&prettyPrint=false' \
  -H 'authority: www.youtube.com' \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.7' \
  -H 'authorization: SAPISIDHASH 1686916263_e46803ac72f6036ba3b55e6edb0e45218c2d9222' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'cookie: CONSENT=PENDING+359; SOCS=CAESEwgDEgk1MDQzNzQ2NDAaAmVuIAEaBgiAhceeBg; DEVICE_INFO=ChxOekU1Tnprd056a3lOalUxTURJd01EQTNOdz09EJ+2kJ8GGJ+2kJ8G; HSID=ACaGQ6WFrIz4Ip9MQ; SSID=AkEQqNjJYkdquRRu6; APISID=c9DHm8ianHgc4LdY/AQMhE_0ECWj0r_orU; SAPISID=a_vNFJhvrDylguw8/Ann5G_jsanpFtW0Pu; __Secure-1PAPISID=a_vNFJhvrDylguw8/Ann5G_jsanpFtW0Pu; __Secure-3PAPISID=a_vNFJhvrDylguw8/Ann5G_jsanpFtW0Pu; LOGIN_INFO=AFmmF2swRQIhANli-SWeYk6WvtIgBzsX4XMeuzlvdXMVtbfJTdhUJPRAAiAlG7PiNiEuUynQLUz5y-t7IvHPtpbmp0sU7_1B8ebQBw:QUQ3MjNmejhuWW5EZV9OVklIOTNxYXpEMXYwQWVvM1ptYTc2OWtObE9TcllyOEc4VndOR0tXVVRUOUhmT2hRbFRkNVZjeVhDRUJ0bmwxcTJTU3ZKWWhvX1hKMFdFbDVBYTdOS2tNMU41ZDI1Y3pIQ2NTVjNrdzJNVGFENDROT2IwdDBTTlV6cmh2RGFWaXpCWndGTHUxMzZBM1NGNk5FbVZn; VISITOR_INFO1_LIVE=swm2xaU6T4s; SID=WwivRnpt9CjuCydglBkAPlpoMnou9Djmu9MIggo5NnkT1-6N69ULSrjryLwj4ZSvzfy6qA.; __Secure-1PSID=WwivRnpt9CjuCydglBkAPlpoMnou9Djmu9MIggo5NnkT1-6NcKwuUDKgPPeuOmwXW3uZUg.; __Secure-3PSID=WwivRnpt9CjuCydglBkAPlpoMnou9Djmu9MIggo5NnkT1-6NIh3P5codR8w_2O6jDK4PVw.; PREF=tz=Europe.Berlin&f6=40000000&f7=100; YSC=nVbKyjjk8dw; __Secure-YEC=CgtuQ2lKWWg3NFhTVSidmbGkBg%3D%3D; SIDCC=AP8dLty32FdokPf_5Qg2eA8TWwebRgwg1n55TG2yQUd-mJkLvroZJj9QGMOIbE33Q2ovqK10H_uA; __Secure-1PSIDCC=AP8dLtz5c8aDk1Gw5VFhcM6EuUcQiZP50kH2XnUIx0PF4bDPWTPwLEq1LhVvadHnHwagqV8DXJI; __Secure-3PSIDCC=AP8dLtzfSXJb4bJhF8czo12Tuc90ONVeuOVXtinx8-_tXE7D4HW1XwHwDfspIBZItbz0aYCjgYDO; ST-txiubb=itct=CCgQ8JMBGAciEwjq7bzg3Mf_AhWjRHoFHezzDzw%3D&csn=MC45MTAyMTY0NjM3ODQ2MTUz&endpoint=%7B%22clickTrackingParams%22%3A%22CCgQ8JMBGAciEwjq7bzg3Mf_AhWjRHoFHezzDzw%3D%22%2C%22commandMetadata%22%3A%7B%22webCommandMetadata%22%3A%7B%22url%22%3A%22%2Fchannel%2FUC8JxlMZ9VPddCuQGwB49fYg%2Fplaylists%22%2C%22webPageType%22%3A%22WEB_PAGE_TYPE_CHANNEL%22%2C%22rootVe%22%3A3611%2C%22apiUrl%22%3A%22%2Fyoutubei%2Fv1%2Fbrowse%22%7D%7D%2C%22browseEndpoint%22%3A%7B%22browseId%22%3A%22UC8JxlMZ9VPddCuQGwB49fYg%22%2C%22params%22%3A%22EglwbGF5bGlzdHPyBgQKAkIA%22%2C%22canonicalBaseUrl%22%3A%22%2Fchannel%2FUC8JxlMZ9VPddCuQGwB49fYg%22%7D%7D; ST-plcuz1=' \
  -H 'origin: https://www.youtube.com' \
  -H 'pragma: no-cache' \
  -H 'referer: https://www.youtube.com/channel/UC8JxlMZ9VPddCuQGwB49fYg/playlists' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: same-origin' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-gpc: 1' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36' \
  -H 'x-goog-authuser: 0' \
  -H 'x-goog-visitor-id: CgtuQ2lKWWg3NFhTVSidmbGkBg%3D%3D' \
  -H 'x-origin: https://www.youtube.com' \
  -H 'x-youtube-bootstrap-logged-in: true' \
  -H 'x-youtube-client-name: 1' \
  -H 'x-youtube-client-version: 2.20230613.01.00' \
  --data-raw '{
   "context":{
      "client":{
         "hl":"de",
         "gl":"DE",
         "remoteHost":"87.123.241.79",
         "deviceMake":"",
         "deviceModel":"",
         "visitorData":"CgtuQ2lKWWg3NFhTVSidmbGkBg%3D%3D",
         "userAgent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36,gzip(gfe)",
         "clientName":"WEB",
         "clientVersion":"2.20230613.01.00",
         "osName":"X11",
         "osVersion":"",
         "originalUrl":"https://www.youtube.com/channel/UC8JxlMZ9VPddCuQGwB49fYg/playlists",
         "platform":"DESKTOP",
         "clientFormFactor":"UNKNOWN_FORM_FACTOR",
         "configInfo":{
            "appInstallData":"CJ2ZsaQGEKXC_hIQzLf-EhDftq8FELq0rwUQvbauBRDbr68FEPOorwUQ4tSuBRDj0f4SEMzfrgUQ7NH-EhDrk64FEI_DrwUQorSvBRDUoa8FEKqy_hIQpZmvBRC4i64FEMyu_hIQscavBRDnuq8FEN62rwUQouyuBRCCna8FEMO3_hIQ1bavBRCMt68FEJCjrwUQ7qKvBRDpw68FEInorgUQl9L-EhD4ta8FEOf3rgUQrLevBRD-ta8FEOSz_hIQ_u6uBQ%3D%3D"
         },
         "userInterfaceTheme":"USER_INTERFACE_THEME_DARK",
         "timeZone":"Europe/Berlin",
         "browserName":"Chrome",
         "browserVersion":"114.0.0.0",
         "acceptHeader":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
         "deviceExperimentId":"ChxOekU1Tnprd056a3lOalUxTURJd01EQTNOdz09EJ2ZsaQGGJ-2kJ8G",
         "screenWidthPoints":1090,
         "screenHeightPoints":980,
         "screenPixelDensity":1,
         "screenDensityFloat":1,
         "utcOffsetMinutes":120,
         "memoryTotalKbytes":"500000",
         "mainAppWebInfo":{
            "graftUrl":"/channel/UC8JxlMZ9VPddCuQGwB49fYg/playlists",
            "pwaInstallabilityStatus":"PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED",
            "webDisplayMode":"WEB_DISPLAY_MODE_BROWSER",
            "isWebNativeShareAvailable":false
         }
      },
      "user":{
         "lockedSafetyMode":false
      },
      "request":{
         "useSsl":true,
         "internalExperimentFlags":[
            
         ],
         "consistencyTokenJars":[
            
         ]
      },
      "clickTracking":{
         "clickTrackingParams":"CCgQ8JMBGAciEwjq7bzg3Mf_AhWjRHoFHezzDzw="
      },
      "adSignalsInfo":{
         "params":[{"key":"dt","value":"1686916254647"},{"key":"flash","value":"0"},{"key":"frm","value":"0"},{"key":"u_tz","value":"120"},{"key":"u_his","value":"14"},{"key":"u_h","value":"1080"},{"key":"u_w","value":"1920"},{"key":"u_ah","value":"1049"},{"key":"u_aw","value":"1866"},{"key":"u_cd","value":"24"},{"key":"bc","value":"31"},{"key":"bih","value":"980"},{"key":"biw","value":"1075"},{"key":"brdim","value":"1280,31,1280,31,1866,31,1866,1049,1090,980"},{"key":"vis","value":"1"},{"key":"wgl","value":"true"},{"key":"ca_type","value":"image"}]
      }
   },
   "browseId":"UC8JxlMZ9VPddCuQGwB49fYg",
   "params":"EglwbGF5bGlzdHPyBgQKAkIA"
}' \
  --compressed
```


# No Results

## Request

```curl
curl 'https://www.youtube.com/youtubei/v1/browse?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&prettyPrint=false' \
  -H 'authority: www.youtube.com' \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.7' \
  -H 'authorization: SAPISIDHASH 1686916270_9e68abaf319d6994e84c3b64f46a2f6b91258f26' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'cookie: CONSENT=PENDING+359; SOCS=CAESEwgDEgk1MDQzNzQ2NDAaAmVuIAEaBgiAhceeBg; DEVICE_INFO=ChxOekU1Tnprd056a3lOalUxTURJd01EQTNOdz09EJ+2kJ8GGJ+2kJ8G; HSID=ACaGQ6WFrIz4Ip9MQ; SSID=AkEQqNjJYkdquRRu6; APISID=c9DHm8ianHgc4LdY/AQMhE_0ECWj0r_orU; SAPISID=a_vNFJhvrDylguw8/Ann5G_jsanpFtW0Pu; __Secure-1PAPISID=a_vNFJhvrDylguw8/Ann5G_jsanpFtW0Pu; __Secure-3PAPISID=a_vNFJhvrDylguw8/Ann5G_jsanpFtW0Pu; LOGIN_INFO=AFmmF2swRQIhANli-SWeYk6WvtIgBzsX4XMeuzlvdXMVtbfJTdhUJPRAAiAlG7PiNiEuUynQLUz5y-t7IvHPtpbmp0sU7_1B8ebQBw:QUQ3MjNmejhuWW5EZV9OVklIOTNxYXpEMXYwQWVvM1ptYTc2OWtObE9TcllyOEc4VndOR0tXVVRUOUhmT2hRbFRkNVZjeVhDRUJ0bmwxcTJTU3ZKWWhvX1hKMFdFbDVBYTdOS2tNMU41ZDI1Y3pIQ2NTVjNrdzJNVGFENDROT2IwdDBTTlV6cmh2RGFWaXpCWndGTHUxMzZBM1NGNk5FbVZn; VISITOR_INFO1_LIVE=swm2xaU6T4s; SID=WwivRnpt9CjuCydglBkAPlpoMnou9Djmu9MIggo5NnkT1-6N69ULSrjryLwj4ZSvzfy6qA.; __Secure-1PSID=WwivRnpt9CjuCydglBkAPlpoMnou9Djmu9MIggo5NnkT1-6NcKwuUDKgPPeuOmwXW3uZUg.; __Secure-3PSID=WwivRnpt9CjuCydglBkAPlpoMnou9Djmu9MIggo5NnkT1-6NIh3P5codR8w_2O6jDK4PVw.; PREF=tz=Europe.Berlin&f6=40000000&f7=100; YSC=nVbKyjjk8dw; __Secure-YEC=CgtuQ2lKWWg3NFhTVSidmbGkBg%3D%3D; SIDCC=AP8dLtxamg1oLrM-gw2tCtJfMUighwYfCtCfwGT6G39nrxXXhtRoBcacfSPMOQwAOIN0xyOUSLyb; __Secure-1PSIDCC=AP8dLtxZ3YHCdW5cYDDaNKO8wvAGqqy4Kp7_xZtEYQW5bryvlEuU2iuJArAJskwLMwqiCznn038; __Secure-3PSIDCC=AP8dLtywHnuXOD7p59fWeUsQXp6MpPsJgZiUgW5ydTzajVvM6w64k4u7aE5WIuB5InMlTNJzKGGK; ST-plcuz1=; ST-ximm1t=csn=MC43NjY5NTkyNzczNjg1NjUy&itct=CCkQui8iEwi3hYnl3Mf_AhU7zBEIHQ_pA8o%3D&endpoint=%7B%22clickTrackingParams%22%3A%22CCkQui8iEwi3hYnl3Mf_AhU7zBEIHQ_pA8o%3D%22%2C%22commandMetadata%22%3A%7B%22webCommandMetadata%22%3A%7B%22url%22%3A%22%2Fchannel%2FUC8JxlMZ9VPddCuQGwB49fYg%2Fplaylists%3Fview%3D1%22%2C%22webPageType%22%3A%22WEB_PAGE_TYPE_CHANNEL%22%2C%22rootVe%22%3A3611%2C%22apiUrl%22%3A%22%2Fyoutubei%2Fv1%2Fbrowse%22%7D%7D%2C%22browseEndpoint%22%3A%7B%22browseId%22%3A%22UC8JxlMZ9VPddCuQGwB49fYg%22%2C%22params%22%3A%22EglwbGF5bGlzdHMgAQ%253D%253D%22%2C%22canonicalBaseUrl%22%3A%22%2Fchannel%2FUC8JxlMZ9VPddCuQGwB49fYg%22%7D%7D' \
  -H 'origin: https://www.youtube.com' \
  -H 'pragma: no-cache' \
  -H 'referer: https://www.youtube.com/channel/UC8JxlMZ9VPddCuQGwB49fYg/playlists?view=1' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: same-origin' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-gpc: 1' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36' \
  -H 'x-goog-authuser: 0' \
  -H 'x-goog-visitor-id: CgtuQ2lKWWg3NFhTVSidmbGkBg%3D%3D' \
  -H 'x-origin: https://www.youtube.com' \
  -H 'x-youtube-bootstrap-logged-in: true' \
  -H 'x-youtube-client-name: 1' \
  -H 'x-youtube-client-version: 2.20230613.01.00' \
  --data-raw '{
   "context":{
      "client":{
         "hl":"de",
         "gl":"DE",
         "remoteHost":"87.123.241.79",
         "deviceMake":"",
         "deviceModel":"",
         "visitorData":"CgtuQ2lKWWg3NFhTVSidmbGkBg%3D%3D",
         "userAgent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36,gzip(gfe)",
         "clientName":"WEB",
         "clientVersion":"2.20230613.01.00",
         "osName":"X11",
         "osVersion":"",
         "originalUrl":"https://www.youtube.com/channel/UC8JxlMZ9VPddCuQGwB49fYg/playlists?view=1",
         "platform":"DESKTOP",
         "clientFormFactor":"UNKNOWN_FORM_FACTOR",
         "configInfo":{
            "appInstallData":"CJ2ZsaQGEKXC_hIQzLf-EhDftq8FELq0rwUQvbauBRDbr68FEPOorwUQ4tSuBRDj0f4SEMzfrgUQ7NH-EhDrk64FEI_DrwUQorSvBRDUoa8FEKqy_hIQpZmvBRC4i64FEMyu_hIQscavBRDnuq8FEN62rwUQouyuBRCCna8FEMO3_hIQ1bavBRCMt68FEJCjrwUQ7qKvBRDpw68FEInorgUQl9L-EhD4ta8FEOf3rgUQrLevBRD-ta8FEOSz_hIQ_u6uBQ%3D%3D"
         },
         "userInterfaceTheme":"USER_INTERFACE_THEME_DARK",
         "timeZone":"Europe/Berlin",
         "browserName":"Chrome",
         "browserVersion":"114.0.0.0",
         "acceptHeader":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
         "deviceExperimentId":"ChxOekU1Tnprd056a3lOalUxTURJd01EQTNOdz09EJ2ZsaQGGJ-2kJ8G",
         "screenWidthPoints":1090,
         "screenHeightPoints":980,
         "screenPixelDensity":1,
         "screenDensityFloat":1,
         "utcOffsetMinutes":120,
         "memoryTotalKbytes":"500000",
         "mainAppWebInfo":{
            "graftUrl":"/channel/UC8JxlMZ9VPddCuQGwB49fYg/playlists?view=1",
            "pwaInstallabilityStatus":"PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED",
            "webDisplayMode":"WEB_DISPLAY_MODE_BROWSER",
            "isWebNativeShareAvailable":false
         }
      },
      "user":{
         "lockedSafetyMode":false
      },
      "request":{
         "useSsl":true,
         "internalExperimentFlags":[
            
         ],
         "consistencyTokenJars":[
            
         ]
      },
      "clickTracking":{
         "clickTrackingParams":"CCkQui8iEwi3hYnl3Mf_AhU7zBEIHQ_pA8o="
      },
      "adSignalsInfo":{
         "params":[{"key":"dt","value":"1686916254647"},{"key":"flash","value":"0"},{"key":"frm","value":"0"},{"key":"u_tz","value":"120"},{"key":"u_his","value":"15"},{"key":"u_h","value":"1080"},{"key":"u_w","value":"1920"},{"key":"u_ah","value":"1049"},{"key":"u_aw","value":"1866"},{"key":"u_cd","value":"24"},{"key":"bc","value":"31"},{"key":"bih","value":"980"},{"key":"biw","value":"1075"},{"key":"brdim","value":"1280,31,1280,31,1866,31,1866,1049,1090,980"},{"key":"vis","value":"1"},{"key":"wgl","value":"true"},{"key":"ca_type","value":"image"}]
      }
   },
   "browseId":"UC8JxlMZ9VPddCuQGwB49fYg",
   "params":"EglwbGF5bGlzdHMgAQ%3D%3D"
}' \
  --compressed
  ```

# Potentially relevant difference

difference | Result | No Result
referer | https://www.youtube.com/channel/UC8JxlMZ9VPddCuQGwB49fYg/playlists | https://www.youtube.com/channel/UC8JxlMZ9VPddCuQGwB49fYg/playlists?view=1
`"originalURL"` | https://www.youtube.com/channel/UC8JxlMZ9VPddCuQGwB49fYg/playlists | https://www.youtube.com/channel/UC8JxlMZ9VPddCuQGwB49fYg/playlists?view=1

## What I think the problem is

I think the problem arises, because the request is made in the wrong manner. Refering to the by the endpoint returned data from earlier, the data is given in pretty much the same format.

Now the thing is, that there are some Topic Channels, where you can't switch the playlist type.

- https://www.youtube.com/channel/UCPOUrPpYMpxQU_gKtBQZroQ/playlists
- https://www.youtube.com/channel/UCV0Ntl3lVR7xDXKoCU6uUXA/playlists

But then there are those Topic Channels, where you actually can switch the playlist type. These are usually the bigger ones. I haven't found why that difference exists though.

- https://www.youtube.com/channel/UC8JxlMZ9VPddCuQGwB49fYg/playlists
- https://www.youtube.com/channel/UCedvOgsKFzcK3hA5taf3KoQ/playlists

So modifying the requests from one of those channels, that currently do yield results, to have the `?view=1` parameter in the url, they still yield results. So my bet right now would be, that the reasons some channels do yield results and some don't is, because invidious makes the requests with `?view=1`, or does something simmilar, which causes the same behaviour.
