def batch_apply(property, n_applications, use_fakes=True):
    start_time = time.time()

    # generate a list of real and fake identities to apply with:
    application_set = [
        Identity("Martin", "Hoffmann", "m.hoffmann@systemli.org"),
        Identity("Martin", "Hoffmann", "m.hoffmann+92@systemli.org"),
        Identity("Martin", "Hoffmann", "m.hoffmann+berlin@systemli.org"),
    ]

    for i in range(n_applications):
        email = f"martin.hoffmann98+{i+1}@systemli.org"
        application_set.append(Identity("Martin", "Hoffmann", email))

        if not use_fakes:
            continue
        for _ in range(random.randint(0, 3)):
            application_set.append(Identity())  # add some fake identities inbetween

    # apply with the given identities:
    for id in application_set:
        status_code, status_text = property.apply(id)
        logging.info(f"{id} {property.id} {status_code} {status_text}")
        time.sleep(random.randint(2, 5))

    delta = time.time() - start_time
    logging.info(f"Sent {len(application_set)} applications in {delta:.1f}s.")
