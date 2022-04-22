# w3bunny - TODOs

[Check README](https://github.com/inaddy/w3bunny/blob/master/README.md)

###1. Production Ready

- [ ] Generate 404 errors
 - [ ] Unsubscribe: Check if queue is bound to exchange.
 - [ ] Retrieve: Check if queue exists. Check if queue is bound to exchange.
- [ ] Test all possible commands combination
- [ ] Stress test code's scalability (single thread i/o loop)
- [ ] Make sure code isn't blocking inside tornado's i/o loop
- [ ] Handle errors (AMQP connection lost, AMQP channel lost)
- [ ] Remove stdout messages and use logging mechanism
- [ ] Deploy in HA scenario (HAproxy like) and fix problems
- [ ] Turn Tornado App into daemon

###2. Code Improvement

- [ ] Remove one AMQP connection per request
- [ ] Close AMQP file descriptors (connections) after request was handled
- [ ] FuncGraph checking for optimisations
