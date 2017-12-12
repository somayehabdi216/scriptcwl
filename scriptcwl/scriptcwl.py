import os
import glob
import logging
import shutil

from schema_salad.validate import ValidationException

from .step import Step, PackedWorkflowException


def load_cwl(fname):
    """Load and validate CWL file using cwltool
    """
    (document_loader, workflowobj, uri) = fetch_document(tmpfile)
    (document_loader, _, processobj, metadata, uri) = \
        validate_document(document_loader, workflowobj, uri)


def load_steps(working_dir=None, steps_dir=None, step_file=None,
               step_list=None):
    """Return a dictionary containing Steps read from file.

    Args:
        steps_dir (str, optional): path to directory containing CWL files.
        step_file (str, optional): path or http(s) url to a single CWL file.
        step_list (list, optional): a list of directories, urls or local file
            paths to CWL files or directories containing CWL files.

    Return:
        dict containing (name, Step) entries.

    """
    if steps_dir is not None:
        step_files = glob.glob(os.path.join(steps_dir, '*.cwl'))
    elif step_file is not None:
        step_files = [step_file]
    elif step_list is not None:
        step_files = []
        for path in step_list:
            if os.path.isdir(path):
                step_files += glob.glob(os.path.join(path, '*.cwl'))
            else:
                step_files.append(path)
    else:
        step_files = []

    steps = {}
    for f in step_files:
        if working_dir is not None:
            # Copy file to working_dir
            if not working_dir == os.path.dirname(f) and not is_url(f):
                copied_file = os.path.join(working_dir, os.path.basename(f))
                shutil.copy2(f, copied_file)

        # Create steps from orgininal files
        try:
            s = Step(f)
            steps[s.name] = s
        except (NotImplementedError, ValidationException,
                PackedWorkflowException) as e:
            logging.warning(e)

    return steps


def is_url(path):
    return path.startswith('http://') or path.startswith('https://')
