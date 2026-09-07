import json
import subprocess
import shlex
import urllib.request
from pathlib import Path

STORE = 'qzrz1p-yz.myshopify.com'
SRC = Path(r'G:/My Drive/Technovators Finance LLC/Shopify/DantheHikingMan/Products')
PRICE = '29.99'
VENDOR = 'DanTheHikingMan'
TAGS = ['hiking', 'apparel', 'dan-the-hiking-man']

PRODUCTS = [
    {'filename': 'Gemini_Generated_Image_en8khwen8khwen8k.jpg', 'title': 'The Original Inspiration Tee', 'handle': 'the-original-inspiration-tee', 'description': 'Classic hiking-inspired graphic tee for the DantheHikingMan collection.'},
    {'filename': 'Gemini_Generated_Image_qvf8e6qvf8e6qvf8 (1).jpg', 'title': 'Oahu Trail Explorer Tee', 'handle': 'oahu-trail-explorer-tee', 'description': 'Island trail energy with a bold hiking graphic built for everyday wear.'},
    {'filename': 'Gemini_Generated_Image_qvf8e6qvf8e6qvf8 (2).jpg', 'title': 'Sequoia Giant Tree Journey Tee', 'handle': 'sequoia-giant-tree-journey-tee', 'description': 'Forest-forward hiking art inspired by giant trees and long trail days.'},
    {'filename': 'Gemini_Generated_Image_qvf8e6qvf8e6qvf8.jpg', 'title': 'Original Inspiration Sunset Tee', 'handle': 'original-inspiration-sunset-tee', 'description': 'A retro sunset hiking tee built around the DanTheHikingMan brand.'},
    {'filename': 'Gemini_Generated_Image_rsoe4prsoe4prsoe (1).jpg', 'title': 'Dan The Hiking Man Hiking Apparel Tee', 'handle': 'dan-the-hiking-man-hiking-apparel-tee', 'description': 'A simple branded tee for hikers, trailheads, and weekend adventures.'},
    {'filename': 'Gemini_Generated_Image_rsoe4prsoe4prsoe (2).jpg', 'title': 'Trail Summit Explorer Tee', 'handle': 'trail-summit-explorer-tee', 'description': 'Mountain-inspired hiking art for people who chase the next summit.'},
    {'filename': 'Gemini_Generated_Image_rsoe4prsoe4prsoe (3).jpg', 'title': 'Hiking Peaks Tee', 'handle': 'hiking-peaks-tee', 'description': 'A clean peak-climbing graphic with strong vintage outdoor style.'},
    {'filename': 'Gemini_Generated_Image_rsoe4prsoe4prsoe (4).jpg', 'title': 'Night Hiker Apparel Tee', 'handle': 'night-hiker-apparel-tee', 'description': 'A moonlit night-hike design for hikers who love after-dark trails.'},
    {'filename': 'Gemini_Generated_Image_rsoe4prsoe4prsoe (5).jpg', 'title': 'DanTheHikingMan Crest Tee', 'handle': 'danthehikingman-crest-tee', 'description': 'Brand crest tee with a vintage badge look for the DantheHikingMan line.'},
    {'filename': 'Gemini_Generated_Image_rsoe4prsoe4prsoe.jpg', 'title': 'The Original Inspiration Retro Tee', 'handle': 'the-original-inspiration-retro-tee', 'description': 'Another version of the original inspiration art with a retro outdoor feel.'},
    {'filename': 'Gemini_Generated_Image_sufnj1sufnj1sufn (1).jpg', 'title': 'Chasing Ridgelines Tee', 'handle': 'chasing-ridgelines-tee', 'description': 'A ridgeline hiking tee built for vistas, climbs, and adventurous days out.'},
    {'filename': 'Gemini_Generated_Image_sufnj1sufnj1sufn (2).jpg', 'title': 'Standing Among Giants Tee', 'handle': 'standing-among-giants-tee', 'description': 'A giant-tree trail tee with bold typography and outdoor identity.'},
    {'filename': 'Gemini_Generated_Image_sufnj1sufnj1sufn (3).jpg', 'title': 'Wilderness Route Tee', 'handle': 'wilderness-route-tee', 'description': 'A rugged route-inspired shirt for trailblazers and explorers.'},
    {'filename': 'Gemini_Generated_Image_sufnj1sufnj1sufn (4).jpg', 'title': 'Finding My Edge Tee', 'handle': 'finding-my-edge-tee', 'description': 'A summit-by-summit hiking tee with a city-meets-trail outlook.'},
    {'filename': 'Gemini_Generated_Image_sufnj1sufnj1sufn.jpg', 'title': 'The Mountains Are Calling Tee', 'handle': 'the-mountains-are-calling-tee', 'description': 'A classic mountain call tee for hikers who live for the next climb.'},
]


def run_shopify(query, variables=None, allow_mutations=False):
    cmd = [
        'bash', '-lc',
        ' '.join([
            'C:/shopify-global/shopify', 'store', 'execute',
            '--store', shlex.quote(STORE),
            '--json',
            ('--allow-mutations' if allow_mutations else ''),
            '--query', shlex.quote(query),
            *(['--variables', shlex.quote(json.dumps(variables))] if variables is not None else []),
        ])
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f'Shopify CLI failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}')
    return json.loads(res.stdout)


def stage_upload(filename):
    query = 'mutation stagedUploadsCreate($input: [StagedUploadInput!]!) { stagedUploadsCreate(input: $input) { stagedTargets { url resourceUrl parameters { name value } } userErrors { field message } } }'
    variables = {'input': [{'filename': filename, 'mimeType': 'image/jpeg', 'resource': 'IMAGE', 'httpMethod': 'PUT'}]}
    data = run_shopify(query, variables=variables, allow_mutations=True)
    payload = data['stagedUploadsCreate']
    if payload['userErrors']:
        raise RuntimeError(f'Staged upload error for {filename}: {payload["userErrors"]}')
    return payload['stagedTargets'][0]


def upload_file(target, file_path):
    headers = {item['name']: item['value'] for item in target['parameters']}
    req = urllib.request.Request(target['url'], data=file_path.read_bytes(), method='PUT')
    for key, value in headers.items():
        if key.lower() != 'content_type':
            req.add_header(key, value)
    if 'content_type' in headers:
        req.add_header('Content-Type', headers['content_type'])
    with urllib.request.urlopen(req, timeout=120) as resp:
        if resp.status not in (200, 201):
            raise RuntimeError(f'Unexpected upload status {resp.status} for {file_path.name}')


def create_product(product, media_source):
    query = (
        'mutation CreateProductWithMedia($product: ProductCreateInput!, $media: [CreateMediaInput!]) '
        '{ productCreate(product: $product, media: $media) { product { id title handle variants(first: 1) { nodes { id price } } media(first: 1) { nodes { id alt mediaContentType } } } userErrors { field message } } }'
    )
    variables = {
        'product': {
            'title': product['title'],
            'handle': product['handle'],
            'vendor': VENDOR,
            'status': 'ACTIVE',
            'productType': 'T-Shirts',
            'descriptionHtml': f"<p>{product['description']}</p><p>Made to showcase the DantheHikingMan adventure brand.</p>",
            'tags': TAGS,
        },
        'media': [
            {
                'originalSource': media_source,
                'alt': product['title'],
                'mediaContentType': 'IMAGE',
            }
        ],
    }
    data = run_shopify(query, variables=variables, allow_mutations=True)
    payload = data['productCreate']
    if payload['userErrors']:
        raise RuntimeError(f'Product create error for {product["handle"]}: {payload["userErrors"]}')
    return payload['product']


def update_variant_price(product_id, variant_id):
    query = (
        'mutation UpdateVariantPrice($productId: ID!, $variants: [ProductVariantsBulkInput!]!) '
        '{ productVariantsBulkUpdate(productId: $productId, variants: $variants) { productVariants { id price } userErrors { field message } } }'
    )
    variables = {'productId': product_id, 'variants': [{'id': variant_id, 'price': PRICE}]}
    data = run_shopify(query, variables=variables, allow_mutations=True)
    payload = data['productVariantsBulkUpdate']
    if payload['userErrors']:
        raise RuntimeError(f'Variant update error for {product_id}: {payload["userErrors"]}')
    return payload['productVariants'][0]


def publish_to_current_channel(product_id):
    query = (
        'mutation PublishToCurrentChannel($id: ID!) '
        '{ publishablePublishToCurrentChannel(id: $id) { '
        'publishable { ... on Product { id title publishedAt } } '
        'userErrors { field message } } }'
    )
    data = run_shopify(query, variables={'id': product_id}, allow_mutations=True)
    payload = data['publishablePublishToCurrentChannel']
    if payload['userErrors']:
        raise RuntimeError(f'Publish error for {product_id}: {payload["userErrors"]}')
    return payload['publishable']


def main():
    existing = run_shopify('query { products(first: 250) { nodes { handle id } } }')['products']['nodes']
    existing_by_handle = {node['handle']: node['id'] for node in existing}
    existing_handles = set(existing_by_handle)
    created = []
    skipped = []

    for index, product in enumerate(PRODUCTS, 1):
        if product['handle'] in existing_handles:
            print(f'skip {index}/15 {product["title"]} (exists)')
            publish_to_current_channel(existing_by_handle[product['handle']])
            skipped.append(product['handle'])
            continue
        file_path = SRC / product['filename']
        print(f'staging {index}/15 {product["title"]}')
        target = stage_upload(product['filename'])
        upload_file(target, file_path)
        print(f'creating {index}/15 {product["title"]}')
        created_product = create_product(product, target['resourceUrl'])
        variant = created_product['variants']['nodes'][0]
        sku = product['handle'].replace('-', '').upper()[:20]
        update_variant_price(created_product['id'], variant['id'])
        publish_to_current_channel(created_product['id'])
        existing_handles.add(product['handle'])
        created.append({
            'title': product['title'],
            'handle': product['handle'],
            'id': created_product['id'],
            'variant_id': variant['id'],
        })
        print(f'created {index}/15 {product["title"]}')

    print('\nSUMMARY')
    print(json.dumps({'created': created, 'skipped': skipped}, indent=2))


if __name__ == '__main__':
    main()
