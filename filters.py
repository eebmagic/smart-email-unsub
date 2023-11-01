import json
import base64

TRUNCATION_SIZE = 1_000

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

    if len(output['body']) < TRUNCATION_SIZE:
        output['body-truncated'] = None
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

            # print(f"Stopped early for msg:")
            # print(json.dumps(msg, indent=2))

        else:
            # print(f"\nFOUND MESSAGE WITH PARTS:")
            # print(json.dumps(lastPart, indent=2))
            # for part in msg['payload']['parts']:
            #     print(json.dumps(getHeaders(part), indent=2))

            foundPlain = False
            for part in msg['payload']['parts']:
                partHeaders = getHeaders(part)
                if 'text/plain' in partHeaders['Content-Type'].lower():
                    body = part['body']
                    package = packageBody(body, partHeaders['Content-Type'])
                    for key, value in package.items():
                        output[key] = value
                    foundPlain = True
                    # print(f"Added plain text part")
            
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
                        # print(f"Added html part")
            
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
                                # print(f"Added multipart part")
                                break
            
            if not foundMulti and not foundPlain and not foundHtml:
                print(f"FAILED TO ADD A PART")
                print([foundPlain, foundHtml, foundMulti])
                print(json.dumps(msg, indent=2))

                    
                    
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


if __name__ == '__main__':
    with open('message_samples.json') as file:
        messages = json.load(file)

    # single = messages[0]
    # result = getMeta(single)


    result = filterMeta(messages)

    print(json.dumps(result, indent=2))

