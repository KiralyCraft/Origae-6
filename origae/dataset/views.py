from __future__ import absolute_import

import flask
import werkzeug.exceptions

from . import images as dataset_images
from . import audio as dataset_audio
from . import text as dataset_text
from . import generic
from origae import extensions
from origae.utils.routing import job_from_request, request_wants_json
from origae.webapp import scheduler

blueprint = flask.Blueprint(__name__, __name__)


def get_actual_job_view(job):
    if isinstance(job, dataset_images.ImageClassificationDatasetJob):
        return dataset_images.classification.views
    elif isinstance(job, dataset_images.GenericImageDatasetJob):
        return dataset_images.generic.views
    elif isinstance(job, dataset_audio.AudioFeatureExtractionDatasetJob):
        return dataset_audio.AudioFeatureExtractionDatasetJob.views
    elif isinstance(job, dataset_audio.GenericAudioDatasetJob):
        return dataset_audio.GenericAudioDatasetJob.views
    elif isinstance(job, dataset_text.TextClassificationDatasetJob):
        return dataset_text.classification.views
    elif isinstance(job, dataset_text.GenericTextDatasetJob):
        return dataset_text.generic.views
    elif isinstance(job, generic.GenericDatasetJob):
        return generic.views
    else:
        raise werkzeug.exceptions.BadRequest('Invalid job type')


@blueprint.route('/<job_id>.json', methods=['GET'])
@blueprint.route('/<job_id>', methods=['GET'])
def show(job_id):
    """
    Show a DatasetJob

    Returns JSON when requested:
        {id, name, directory, status}
    """
    job = scheduler.get_job(job_id)
    if job is None:
        raise werkzeug.exceptions.NotFound('Job not found')

    related_jobs = scheduler.get_related_jobs(job)

    if request_wants_json():
        return flask.jsonify(job.json_dict(True))
    else:
        views = get_actual_job_view(job)
        views.show(job, related_jobs=related_jobs)


@blueprint.route('/summary', methods=['GET'])
def summary():
    """
    Return a short HTML summary of a DatasetJob
    """
    job = job_from_request()
    views = get_actual_job_view(job)
    views.summary(job)


@blueprint.route('/inference-form/<extension_id>/<job_id>', methods=['GET'])
def inference_form(extension_id, job_id):
    """
    Returns a rendering of an inference form
    """
    inference_form_html = ""

    if extension_id != "all-default":
        extension_class = extensions.data.get_extension(extension_id)
        if not extension_class:
            raise RuntimeError("Unable to find data extension with ID=%s"
                               % job_id.dataset.extension_id)
        job = scheduler.get_job(job_id)
        if hasattr(job, 'extension_userdata'):
            extension_userdata = job.extension_userdata
        else:
            extension_userdata = {}
        extension_userdata.update({'is_inference_db': True})
        extension = extension_class(**extension_userdata)

        form = extension.get_inference_form()
        if form:
            template, context = extension.get_inference_template(form)
            inference_form_html = flask.render_template_string(template, **context)

    return inference_form_html
