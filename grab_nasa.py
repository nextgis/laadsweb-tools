# grab_fucking_nasa
import requests

WEB_API_FILES = 'https://ladsweb.modaps.eosdis.nasa.gov/api/v1/files/product={0}&collection={1}&dateRanges={2}..{3}&areaOfInterest=x{4}y{5},x{6}y{7}&dayCoverage={8}'
WEB_API_PREVIEWS = 'https://ladsweb.modaps.eosdis.nasa.gov/api/v1/imageFiles/'


def get_images(product, collection, date_begin, date_end, area, day_coverage):
    """
    Get array of images and previews

    :param product: Example 'MOD02QKM'
    :param collection: Example '6'
    :param date_begin: Example '2017-07-01'
    :param date_end: Example '2017-08-03'
    :param area: Set of coords: (x_min, y_min, x_max, y_max)
    :param day_coverage: 'true' or 'false'
    :return:
    """
    session = requests.session()

    # get images
    image_url = WEB_API_FILES.format(product, collection, date_begin, date_end, area[0], area[1], area[2], area[3], day_coverage)
    img_resp = session.get(image_url).json()

    # get previews
    ids = img_resp.keys()
    prev_resp = session.post(WEB_API_PREVIEWS, data={'fileIds': str(','.join(ids)),}).json()

    # make dict
    result = {}
    for key,image_info in img_resp.items():
        result[key] = {
            'name': image_info['name'],
            'image_url': image_info['fileURL'],
            'prev_url': prev_resp[key][0]['URL'] + '\/' + prev_resp[key][0]['FileName'] if key in prev_resp.keys() else None
        }

    return result

images = get_images('MOD02QKM', 6, '2017-08-02', '2017-09-13', (44.1, 47.3, 47.6, 44.4), 'true')

print(images)

for k,v in images.items():
    name = v['name']