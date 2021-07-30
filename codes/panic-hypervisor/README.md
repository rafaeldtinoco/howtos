## Panic'ing a hypervisor by QEMU triggers

So, I had these scripts saved for sometime now and forgot to share: doing it
now. I cannot think on why this would be useful for anyone not in a
Sustaining Engineering team, just as I was (at Canonical) when created them,
but feel free to play with it.

> These scripts might help you debug hypervisor issues whenever a guest panics.

Yes, you did not read it wrong =). Idea is simple: sometimes the hypervisor
missbehaves, causing big latency to a guest, let's say, and you might be
interested in panic'ing the host - cannot think of anything else than for a
kdump analysis - at the exact moment something happens inside a guest, right ?

Problem is that *the exact moment* in CPU terms is not the *exact moment*, and
any script that you might do that monitors the guest and panics the host might
cause enough CPU work that the situation within the hypervisor might already
be gone in the kdump you will be able to get.

So... with these systemtap scripts you will:

- Run a systemtap script in the host that will hear from guest using emulated
  ttyS0 device. whenever the guest writes to a specific ttyS0 port it will
  panic the host. Don't worry, this address is not used by /dev/ttyS0
  emulation so you won't have your system panic'ed by regular serial text.

- Run a systemtap script in the guest that will, like said above, write to a
  special ttyS0 address and cause the host to execute __asm("int $13"), which
  will cause kexec/kdump logic to be triggered.

With this, you will be VERY close to having what you want:

1. QEMU guest trigger (that might be anything you want)
2. EXACT hypervisor CPU stacks, so you can dive into what is wrong

I hope this helps others as it did help me in the past. I was able to verify
rcu locking bugs in the kernel hypervisor, prove resource contention on memory
pages reclaiming - because of fragmentation or usage - to others, and dig into
all kinds of things we usually dig analysing kdumps.


Have fun!



