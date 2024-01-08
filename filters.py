import json
import base64
import re

TRUNCATION_SIZE = 1_000

def getDollarAmounts(body):
    dollarRegex = re.compile(r'\$\d{1,3}(,?\d{3})*(\.\d{2})?')
    finditer = dollarRegex.finditer(body)

    groups = [match.group() for match in finditer]

    return ' '.join(set(groups))


def getHeaders(part):
    headers = {}
    for header in part['headers']:
        headers[header['name']] = header['value']

    return headers


def packageBody(body, contentType):
    output = {
        'body-type': contentType,
        'body-size': body['size'],
        'body-encoded': body['data'],
        'body': base64.urlsafe_b64decode(body['data']).decode('utf-8')
    }

    output['dollar-amounts'] = getDollarAmounts(output['body'])

    if len(output['body']) < TRUNCATION_SIZE:
        output['body-truncated'] = False
    else:
        output['body-truncated'] = output['body'][:TRUNCATION_SIZE]

    return output


def getMeta(msg):
    output = {}

    tags = [
        'id',
        'threadId',
        'snippet',
        'sizeEstimate',
        'internalDate'
    ]

    headers = [
        'Delivered-To',
        'Return-Path',
        'Date',
        'From',
        'To',
        'From',
        'Subject',
        'Content-Type',
        'Content-Transfer-Encoding',
    ]

    for tag in tags:
        output[tag] = msg[tag]
    output['url'] = f"https://mail.google.com/mail/u/0/#inbox/{msg['id']}"

    for entry in msg['payload']['headers']:
        if entry['name'] in headers:
            output[entry['name']] = entry['value']

    # Get decoded body
    try:
        if 'parts' not in msg['payload']:
            body = msg['payload']['body']
            package = packageBody(body, output['Content-Type'])
            for key, value in package.items():
                output[key] = value
        else:
            foundPlain = False
            for part in msg['payload']['parts']:
                partHeaders = getHeaders(part)
                if 'text/plain' in partHeaders['Content-Type'].lower():
                    body = part['body']
                    package = packageBody(body, partHeaders['Content-Type'])
                    for key, value in package.items():
                        output[key] = value
                    foundPlain = True

            # As backup add full html
            foundHtml = False
            if not foundPlain:
                for part in msg['payload']['parts']:
                    partHeaders = getHeaders(part)
                    if 'text/html' in partHeaders['Content-Type'].lower():
                        body = part['body']
                        package = packageBody(body, partHeaders['Content-Type'])
                        for key, value in package.items():
                            output[key] = value
                        foundHtml = True
            # Add full html regardless for full urls
            for part in msg['payload']['parts']:
                partHeaders = getHeaders(part)
                if 'text/html' in partHeaders['Content-Type'].lower():
                    body = part['body']
                    package = packageBody(body, output['Content-Type'])
                    output['html'] = package

            foundMulti = False
            if not foundPlain and not foundHtml:
                typeSet = set([getHeaders(part)['Content-Type'] for part in msg['payload']['parts']])
                for partType in typeSet:
                    if 'multipart' in partType.lower():
                        for part in msg['payload']['parts'][0]['parts']:
                            partHeaders = getHeaders(part)
                            if 'text/plain' in partHeaders['Content-Type'].lower():
                                body = part['body']
                                package = packageBody(body, partHeaders['Content-Type'])
                                for key, value in package.items():
                                    output[key] = value
                                foundMulti = True
                                break

            if not foundMulti and not foundPlain and not foundHtml:
                print(f"FAILED TO ADD A PART: {msg['id']}")
                print([foundPlain, foundHtml, foundMulti])
                # print(json.dumps(msg, indent=2))

    except:
        print(f"FAILED TO GET BODY FOR THIS MESSAGE:")
        print(json.dumps(msg, indent=2))


    return output


def filterMeta(messages):
    # return [getMeta(msg) for msg in messages]
    result = []
    for msg in messages:
        result.append(getMeta(msg))
    return result


def getUnsubLinks(text, N=20, COUNT=2):
    whitelist = [
        'unsubscribe',
        'manage',
        'subscription',
        'preferences',
        'communications'
    ]
    def getWeights(toks, direction, whitelist=whitelist):
        binary = []
        for t in toks:
            added = False
            for word in whitelist:
                # if t.lower() in word:
                # if t.lower().strip() == word.strip():
                if word in t.lower().strip():
                    binary.append(True)
                    added=True
                    break
            if not added:
                binary.append(False)

        N = len(toks)
        assert len(binary) == N, "BINARY AND TOKS DIDNT MATCH LEN"
        if direction == 'before':
            denoms = range(N, 0, -1)
        else:
            denoms = range(1, N+1, 1)

        weights = [(1/d if val else 0) for (val, d) in zip(binary, denoms)]
        if len(weights) == 0:
            weights = [0]

        return weights

    # Regex for extracting URLs
    url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    # Find all URLs in the text
    urls = re.findall(url_regex, text)

    # Tokenize the text
    tokens = text.split()

    # Find the indices of the tokens that are URLs
    url_indices = [i for i, token in enumerate(tokens) if re.match(url_regex, token)]

    # Extract N tokens before and after each URL
    contexts = []
    for index in url_indices:
        start = max(0, index - N)  # Ensure the start is not negative
        end = min(len(tokens), index + N + 1)  # Ensure the end does not exceed the length of the tokens
        beforeTokens = tokens[start:index]
        afterTokens = tokens[index + 1:end]
        beforeWeights = getWeights(beforeTokens, 'before')
        afterWeights = getWeights(afterTokens, 'after')
        before = ' '.join(beforeTokens)
        after = ' '.join(afterTokens)

        contexts.append((tokens[index], before, after, max(beforeWeights), max(afterWeights)))

    contexts = filter(
        lambda x: max(x[3], x[4]) > 0,
        contexts
    )

    contexts = sorted(
        contexts,
        key=lambda x: x[3]+x[4],
        reverse=True
    )

    contexts = contexts[:COUNT]

    formatted = [
        {
            'url': context[0],
            'before': context[1],
            'after': context[2],
            'before-weight': context[3],
            'after-weight': context[4]
        }
        for context in contexts
    ]

    return formatted


def getUsefulBodies(messages):
    with open("./frontend/src/links.json.json") as file:
        links = json.load(file)

    ids = []
    bodies = []
    usedMessages = []
    for msg in messages:

        try:
            if len(msg['body']) > 0:
                bodies.append(msg['body'])
            elif ('body-truncated' in msg) and (type(msg['body-truncated']) == str):
                bodies.append(msg['body-truncated'])
            elif ('snippet' in msg) and (len(msg['snippet']) > 0):
                bodies.append(msg['snippet'])
            else:
                bodies.append('NO BODY OR SNIPPET FOUND')

            ids.append(msg['id'])
            for key, value in msg.items():
                if type(value) == dict:
                    msg[key] = json.dumps(value, sort_keys=True)
            links[msg['id']] = getUnsubLinks(msg['body'])
            usedMessages.append(msg)
        except:
            print(f"FAILED TO GET BODY FOR THIS MESSAGE:")
            print(json.dumps(msg, indent=2))

    with open("./frontend/src/links.json.json", 'w') as file:
        json.dump(links, file, indent=2)

    return ids, bodies, usedMessages


if __name__ == '__main__':
    with open('message_samples.json') as file:
        messages = json.load(file)

    # single = messages[0]
    # result = getMeta(single)

    result = filterMeta(messages)

    print(json.dumps(result, indent=2))

