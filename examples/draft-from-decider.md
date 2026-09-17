---
title: "One Camera, Eight Years Behind"
source_id: https://news.ycombinator.com/item?id=49726586
source_url: https://www.wired.com/story/hackers-flock-camera-data-shows-how-system-works/
date: 2026-09-16
status: pending
---
# One Camera, Eight Years Behind

A roadside camera only keeps your data as safe as the software inside it.

I read the article and the sources behind it. A hacker group called stegan0gram took a Flock Safety roadway camera off its pole and copied nearly everything on it. WIRED and 404 Media ran a joint investigation. DDoSecrets published the raw filesystem images.

One camera. Twenty-one days. More than 1.6 million images of about 50,000 vehicles.

The encryption key sat in an unencrypted partition labeled "media." That key opened thousands of stored videos and stills. The software tagged more than plates. It logged people and bicycles, with confidence scores, plus bumper stickers and patches on motorcyclists' bags.

The camera ran Android 8.1, with a security patch from June 2018. Roughly eight years without updates.

Flock Safety said removing the camera was illegal and pointed to its vulnerability disclosure policy.

Picture a locked safe with the key taped to the outside. That is this camera.

One thing to do today. Check the software version on any device that records your home or street. If the vendor cannot tell you the patch date, that is your answer.

A rule you can read in a file beats a promise in a dashboard. Take care.

## Facts used

- A hacker collective calling itself stegan0gram physically removed a Flock Safety roadway camera, copied nearly all of its stored data, and shared the files with WIRED and 404 Media, which ran a joint investigation; the data was also given to DDoSecrets, which published filesystem images of the camera's partitions. — https://www.404media.co/hackers-stole-flocks-camera-software-revealing-how-the-company-tracks-cars-and-people-2/
- Images and logs on the single device showed it captured more than 1.6 million images of roughly 50,000 vehicles over a 21-day period. — https://san.com/cc/hackers-stole-a-flock-camera-heres-what-they-found-inside/
- The hackers bypassed encryption by finding an encryption key in an unencrypted partition of the camera's storage labeled 'media', which unlocked thousands of stored vehicle videos and still images. — https://san.com/cc/hackers-stole-a-flock-camera-heres-what-they-found-inside/
- The camera's software detects not only vehicles and license plates but also people and bicycles, recording where a person appears in an image with a confidence score, and logging details such as bumper stickers and patches on motorcyclists' bags. — https://newrepublic.com/post/215485/hacked-data-flock-cameras-recording-people
- Flock Safety responded that 'the unauthorized removal and tampering of a Flock camera is illegal,' said it had not received a vulnerability report from the hackers, and pointed to its public Vulnerability Disclosure Policy. — https://san.com/cc/hackers-stole-a-flock-camera-heres-what-they-found-inside/
- Per the DDoSecrets release, the camera was running Android 8.1 (released 2017, unsupported by Google since 2021) with a security patch level of 2018-06-05, meaning it had gone roughly eight years without Android security updates. — https://ddosecrets.org/article/flock-alpr-camera
