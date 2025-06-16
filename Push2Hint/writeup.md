# Push2Hint

```
Hint: Push!

说明：本题将创建两个实例，请先访问第一个实例，在其中你能得到第二个实例的正确访问方法。本题采用自签名证书，请忽略安全警告后使用https://instance.penguin.0ops.sjtu.cn:<端口>/访问（不需要使用nc）。

Hint: 用惯了curl偶尔尝试些别的工具或许也不错，maybe *n*ina is a *g*ood *http* client.
```

The challenge hints that I should use [nghttp](https://github.com/nghttp2/nghttp2), a cli tool for http2.

Visit the first instance using nghttp: `nghttp -v https://instance.penguin.0ops.sjtu.cn:18714/`, and got result:

```html
[  0.024] Connected
[WARNING] Certificate verification failed: hostname mismatch
The negotiated protocol: h2
[  0.036] send SETTINGS frame <length=12, flags=0x00, stream_id=0>
          (niv=2)
          [SETTINGS_MAX_CONCURRENT_STREAMS(0x03):100]
          [SETTINGS_INITIAL_WINDOW_SIZE(0x04):65535]
[  0.036] send HEADERS frame <length=48, flags=0x05, stream_id=13>
          ; END_STREAM | END_HEADERS
          (padlen=0)
          ; Open new stream
          :method: GET
          :path: /
          :scheme: https
          :authority: instance.penguin.0ops.sjtu.cn:18714
          accept: */*
          accept-encoding: gzip, deflate
          user-agent: nghttp2/1.64.0
[  0.043] recv SETTINGS frame <length=18, flags=0x00, stream_id=0>
          (niv=3)
          [SETTINGS_MAX_CONCURRENT_STREAMS(0x03):128]
          [SETTINGS_INITIAL_WINDOW_SIZE(0x04):65536]
          [SETTINGS_MAX_FRAME_SIZE(0x05):16777215]
[  0.043] recv WINDOW_UPDATE frame <length=4, flags=0x00, stream_id=0>
          (window_size_increment=2147418112)
[  0.043] recv SETTINGS frame <length=0, flags=0x01, stream_id=0>
          ; ACK
          (niv=0)
[  0.043] recv (stream_id=13) :status: 200
[  0.043] recv (stream_id=13) server: nginx/1.25.0
[  0.043] recv (stream_id=13) date: Fri, 04 Apr 2025 15:03:56 GMT
[  0.043] recv (stream_id=13) content-type: text/html
[  0.043] recv (stream_id=13) content-length: 1574
[  0.043] recv (stream_id=13) last-modified: Thu, 27 Feb 2025 16:39:33 GMT
[  0.043] recv (stream_id=13) etag: "67c09545-626"
[  0.043] recv (stream_id=13) accept-ranges: bytes
[  0.043] recv HEADERS frame <length=110, flags=0x04, stream_id=13>
          ; END_HEADERS
          (padlen=0)
          ; First response header
[  0.043] send SETTINGS frame <length=0, flags=0x01, stream_id=0>
          ; ACK
          (niv=0)
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PUSH</title>
</head>
<body>
    <button id="pushButton">push</button>
    <div id="hintContainer"></div>
    <script>
    document.getElementById('pushButton').addEventListener('click', function(){
        var hints = ["Do you know *push*?","You might not know about it, it is *deprecated* a while ago", "I just pushed the *Hint*! Maybe search for this word", "There is no flag inside the gif!"];
        var randomHint = hints[Math.floor(Math.random() * hints.length)];
        alert(randomHint);
        if(!document.getElementById('pushImage')){
            // Create a wrapper for the image and caption
            var wrapper = document.createElement('div');
            wrapper.style.position = 'relative';
            wrapper.style.display = 'inline-block';

            var img = document.createElement('img');
            img.id = 'pushImage';
            img.src = '/push.gif';
            wrapper.appendChild(img);

            var caption = document.createElement('b');
            caption.textContent = 'PUSH';
            caption.style.position = 'absolute';
            caption.style.bottom = '0';
            caption.style.left = '50%';
            caption.style.transform = 'translateX(-50%)';
            caption.style.fontSize = '54px';
            caption.style.color = 'white';
            wrapper.appendChild(caption);

            document.getElementById('hintContainer').appendChild(wrapper);
        }
    });
    </script>
</body>
</html>
[  0.045] recv DATA frame <length=1574, flags=0x01, stream_id=13>
          ; END_STREAM
[  0.045] send GOAWAY frame <length=8, flags=0x00, stream_id=0>
          (last_stream_id=0, error_code=NO_ERROR(0x00), opaque_data(0)=[])
```

Thus run `nghttp -v https://instance.penguin.0ops.sjtu.cn:18714/push.gif > push.gif.txt`, and run `less push.gif.txt` to see the head of that file:

```
[  0.025] Connected
The negotiated protocol: h2
[  0.039] send SETTINGS frame <length=12, flags=0x00, stream_id=0>
          (niv=2)
          [SETTINGS_MAX_CONCURRENT_STREAMS(0x03):100]
          [SETTINGS_INITIAL_WINDOW_SIZE(0x04):65535]
[  0.039] send HEADERS frame <length=56, flags=0x05, stream_id=13>
          ; END_STREAM | END_HEADERS
          (padlen=0)
          ; Open new stream
          :method: GET
          :path: /push.gif
          :scheme: https
          :authority: instance.penguin.0ops.sjtu.cn:18714
          accept: */*
          accept-encoding: gzip, deflate
          user-agent: nghttp2/1.64.0
[  0.044] recv SETTINGS frame <length=18, flags=0x00, stream_id=0>
          (niv=3)
          [SETTINGS_MAX_CONCURRENT_STREAMS(0x03):128]
          [SETTINGS_INITIAL_WINDOW_SIZE(0x04):65536]
          [SETTINGS_MAX_FRAME_SIZE(0x05):16777215]
[  0.044] recv WINDOW_UPDATE frame <length=4, flags=0x00, stream_id=0>
          (window_size_increment=2147418112)
[  0.044] recv SETTINGS frame <length=0, flags=0x01, stream_id=0>
          ; ACK
          (niv=0)
[  0.044] recv (stream_id=13) :method: GET
[  0.044] recv (stream_id=13) :path: /0195183f-2a1d-7fd7-a4b7-08a5406b502b
[  0.044] recv (stream_id=13) :scheme: https
[  0.044] recv (stream_id=13) :authority: instance.penguin.0ops.sjtu.cn:18714
[  0.044] recv (stream_id=13) accept-encoding: gzip, deflate
[  0.044] recv (stream_id=13) user-agent: nghttp2/1.64.0
[  0.044] recv PUSH_PROMISE frame <length=86, flags=0x04, stream_id=13>
          ; END_HEADERS
          (padlen=0, promised_stream_id=2)
[  0.044] recv (stream_id=13) :status: 200
[  0.044] recv (stream_id=13) server: nginx/1.25.0
[  0.044] recv (stream_id=13) date: Fri, 04 Apr 2025 15:06:05 GMT
[  0.044] recv (stream_id=13) content-type: image/gif
[  0.044] recv (stream_id=13) content-length: 1046312
[  0.044] recv (stream_id=13) last-modified: Thu, 27 Feb 2025 16:39:33 GMT
[  0.044] recv (stream_id=13) etag: "67c09545-ff728"
[  0.044] recv (stream_id=13) accept-ranges: bytes
[  0.044] recv HEADERS frame <length=114, flags=0x04, stream_id=13>
          ; END_HEADERS
          (padlen=0)
          ; First response header
[  0.044] send SETTINGS frame <length=0, flags=0x01, stream_id=0>
          ; ACK
          (niv=0)
GIF89a,^A<E7>^@<F7>^@^@^Y^W^T^_^\^Z"%^W-+^Z#9^V^_^\'#&
...
```

Run `nghttp https://instance.penguin.0ops.sjtu.cn:18714/0195183f-2a1d-7fd7-a4b7-08a5406b502b`, and got result:

```
Hint: I hosted the website https://gives.you.hint on the other instance, visit "/r3d1r3ct" to get the final hint! We don't accept old browsers on this one too!
```

An interesting thing is when I ran `nghttp https://instance.penguin.0ops.sjtu.cn:18714/push.gif > push.gif`, and I used Detect-It-Easy tool to inspect the GIF and searched for strings, and also found the above hint text.

Visit instance2: `nghttp -v https://instance.penguin.0ops.sjtu.cn:18198/r3d1r3ct` and got result:

```html
[  0.038] Connected
[WARNING] Certificate verification failed: hostname mismatch
The negotiated protocol: h2
[  0.058] send SETTINGS frame <length=12, flags=0x00, stream_id=0>
          (niv=2)
          [SETTINGS_MAX_CONCURRENT_STREAMS(0x03):100]
          [SETTINGS_INITIAL_WINDOW_SIZE(0x04):65535]
[  0.058] send HEADERS frame <length=56, flags=0x05, stream_id=13>
          ; END_STREAM | END_HEADERS
          (padlen=0)
          ; Open new stream
          :method: GET
          :path: /r3d1r3ct
          :scheme: https
          :authority: instance.penguin.0ops.sjtu.cn:18198
          accept: */*
          accept-encoding: gzip, deflate
          user-agent: nghttp2/1.64.0
[  0.065] recv SETTINGS frame <length=18, flags=0x00, stream_id=0>
          (niv=3)
          [SETTINGS_ENABLE_CONNECT_PROTOCOL(0x08):1]
          [SETTINGS_INITIAL_WINDOW_SIZE(0x04):16384]
          [SETTINGS_MAX_CONCURRENT_STREAMS(0x03):100]
[  0.065] recv SETTINGS frame <length=0, flags=0x01, stream_id=0>
          ; ACK
          (niv=0)
[  0.065] recv (stream_id=13) :status: 403
[  0.065] recv (stream_id=13) content-length: 93
[  0.065] recv (stream_id=13) cache-control: no-cache
[  0.065] recv (stream_id=13) content-type: text/html
[  0.065] recv HEADERS frame <length=30, flags=0x04, stream_id=13>
          ; END_HEADERS
          (padlen=0)
          ; First response header
<html><body><h1>403 Forbidden</h1>
Request forbidden by administrative rules.
</body></html>
[  0.065] recv DATA frame <length=93, flags=0x01, stream_id=13>
          ; END_STREAM
[  0.065] send GOAWAY frame <length=8, flags=0x00, stream_id=0>
          (last_stream_id=0, error_code=NO_ERROR(0x00), opaque_data(0)=[])
```

As hinted, change `Host` header:

`nghttp -v -H ':authority: gives.you.hint' https://instance.penguin.0ops.sjtu.cn:18198/r3d1r3ct`

```html
[  0.022] Connected
[WARNING] Certificate verification failed: hostname mismatch
The negotiated protocol: h2
[  0.031] send SETTINGS frame <length=12, flags=0x00, stream_id=0>
          (niv=2)
          [SETTINGS_MAX_CONCURRENT_STREAMS(0x03):100]
          [SETTINGS_INITIAL_WINDOW_SIZE(0x04):65535]
[  0.031] send HEADERS frame <length=41, flags=0x05, stream_id=13>
          ; END_STREAM | END_HEADERS
          (padlen=0)
          ; Open new stream
          :method: GET
          :path: /r3d1r3ct
          :scheme: https
          :authority: gives.you.hint
          accept: */*
          accept-encoding: gzip, deflate
          user-agent: nghttp2/1.64.0
[  0.038] recv SETTINGS frame <length=18, flags=0x00, stream_id=0>
          (niv=3)
          [SETTINGS_ENABLE_CONNECT_PROTOCOL(0x08):1]
          [SETTINGS_INITIAL_WINDOW_SIZE(0x04):16384]
          [SETTINGS_MAX_CONCURRENT_STREAMS(0x03):100]
[  0.038] recv SETTINGS frame <length=0, flags=0x01, stream_id=0>
          ; ACK
          (niv=0)
[  0.038] recv (stream_id=13) :status: 103
[  0.038] recv (stream_id=13) link: </5uPer_5eCR3t_PatH>; rel=preload; as=fetch
[  0.038] recv HEADERS frame <length=50, flags=0x04, stream_id=13>
          ; END_HEADERS
          (padlen=0)
          ; First response header
[  0.038] send SETTINGS frame <length=0, flags=0x01, stream_id=0>
          ; ACK
          (niv=0)
[  0.042] recv (stream_id=13) :status: 302
[  0.042] recv (stream_id=13) server: Werkzeug/3.1.3 Python/3.12.4
[  0.042] recv (stream_id=13) date: Fri, 04 Apr 2025 15:29:29 GMT
[  0.042] recv (stream_id=13) content-type: text/html; charset=utf-8
[  0.042] recv (stream_id=13) content-length: 239
[  0.042] recv (stream_id=13) location: https://0ops.no.flag.here/
[  0.042] recv HEADERS frame <length=125, flags=0x04, stream_id=13>
          ; END_HEADERS
          (padlen=0)
<!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="https://0ops.no.flag.here/">https://0ops.no.flag.here/</a>. If not, click the link.
[  0.044] recv DATA frame <length=239, flags=0x01, stream_id=13>
          ; END_STREAM
[  0.044] send GOAWAY frame <length=8, flags=0x00, stream_id=0>
          (last_stream_id=0, error_code=NO_ERROR(0x00), opaque_data(0)=[])
```

Run `nghttp -v -H ':authority: gives.you.hint' https://instance.penguin.0ops.sjtu.cn:18198/5uPer_5eCR3t_PatH`:

```html
[  0.016] Connected
[WARNING] Certificate verification failed: hostname mismatch
The negotiated protocol: h2
[  0.027] send SETTINGS frame <length=12, flags=0x00, stream_id=0>
          (niv=2)
          [SETTINGS_MAX_CONCURRENT_STREAMS(0x03):100]
          [SETTINGS_INITIAL_WINDOW_SIZE(0x04):65535]
[  0.027] send HEADERS frame <length=48, flags=0x05, stream_id=13>
          ; END_STREAM | END_HEADERS
          (padlen=0)
          ; Open new stream
          :method: GET
          :path: /5uPer_5eCR3t_PatH
          :scheme: https
          :authority: gives.you.hint
          accept: */*
          accept-encoding: gzip, deflate
          user-agent: nghttp2/1.64.0
[  0.033] recv SETTINGS frame <length=18, flags=0x00, stream_id=0>
          (niv=3)
          [SETTINGS_ENABLE_CONNECT_PROTOCOL(0x08):1]
          [SETTINGS_INITIAL_WINDOW_SIZE(0x04):16384]
          [SETTINGS_MAX_CONCURRENT_STREAMS(0x03):100]
[  0.033] recv SETTINGS frame <length=0, flags=0x01, stream_id=0>
          ; ACK
          (niv=0)
[  0.033] send SETTINGS frame <length=0, flags=0x01, stream_id=0>
          ; ACK
          (niv=0)
[  0.035] recv (stream_id=13) :status: 200
[  0.035] recv (stream_id=13) server: Werkzeug/3.1.3 Python/3.12.4
[  0.035] recv (stream_id=13) date: Fri, 04 Apr 2025 15:32:42 GMT
[  0.035] recv (stream_id=13) content-type: text/html; charset=utf-8
[  0.035] recv (stream_id=13) content-length: 47
[  0.035] recv HEADERS frame <length=92, flags=0x04, stream_id=13>
          ; END_HEADERS
          (padlen=0)
          ; First response header
0ops{600dby3_PU$H_4Nd_54y_he1l0_7o_3@R1y_h!ntS}[  0.035] recv DATA frame <length=47, flags=0x01, stream_id=13>
          ; END_STREAM
[  0.035] send GOAWAY frame <length=8, flags=0x00, stream_id=0>
          (last_stream_id=0, error_code=NO_ERROR(0x00), opaque_data(0)=[])
```

Get flag: `0ops{600dby3_PU$H_4Nd_54y_he1l0_7o_3@R1y_h!ntS}`