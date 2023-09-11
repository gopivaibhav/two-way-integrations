# Two-Way Integrations

This project demonstrates the implementation of a two-way integration system that synchronizes a local customer catalog with an external service, specifically Stripe, in near real-time. The integration is designed to be extendable for future integrations with other catalogs and systems within the product.

## Requirements 

Before getting started, I made these prerequisites as given in the [assignment](https://zenskar.notion.site/Zenskar-Assignment-Back-End-Engineer-Intern-c2b28fa7ed0247008197c09d10ff8532) :

1. **Database**: Created a simple customer table in an SQL-based relational database (using SQLite) with columns (ID, name, email).

2. **Stripe Account**: Set up a free test account on Stripe and added the API_KEY to `.env` file in parent directory with key  '*STRIPE_API_KEY*' to secure my stripe accout.

3. **Queueing System**: I am using ZeroMQ as queueing system.

## Implementation

### Outward Sync (Local to Stripe):

- Changes to customer entries in the product are being made via an API.
- Any changes should be added to the queue for processing.
- Created a worker that listens to the queue and updates corresponding customer data in Stripe.

### Inward Sync (Stripe to Local):

Webhook (I chose Option 2):
- Set up an API server on my local machine.
- Exposed this server as a webhook to Stripe using Ngrok.
- Stripe will send events to this webhook for changes in its customer catalog.
- Processed these events to sync my product's customer catalog.

### Extending for Future Integrations

To extend this integration for additional systems like Salesforce's customer catalog:

- My code is well-structured and modular, with separate components for each integration. So, we can easily understand the code and make the necessary changes to the codebase.


## Conclusion

This project showcases a flexible two-way integration system that synchronizes a local customer catalog with external services like Stripe. With a well-structured and modular codebase, it is easy to extend this system to support additional integrations and other systems within the product.

Feel free to reach out if you have any questions or need further assistance.
