from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import Book
import logging

# Logger setup
logger = logging.getLogger(__name__)


def book_list(request):
    query = request.GET.get('q', '')
    logger.info("Book list accessed. Search query: %s", query)

    books = Book.objects.all()  # soft-deleted hidden automatically
    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
        logger.debug("Filtered books with query: %s", query)

    return render(request, 'library/book_list.html', {'books': books, 'query': query})


def book_add(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        isbn = request.POST.get('isbn', '').strip()
        year = request.POST.get('published_year', '').strip()

        errors = {}
        if not title:
            errors['title'] = 'Title is required'
        if not author:
            errors['author'] = 'Author is required'
        if not year.isdigit():
            errors['published_year'] = 'Year must be a number'

        if errors:
            logger.warning("Book add validation failed. Errors: %s", errors)
            return render(request, 'library/book_form.html',
                          {'errors': errors, 'data': request.POST, 'action': 'Add'})

        book = Book.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            published_year=int(year)
        )

        logger.info("New book created. ID: %s, Title: %s", book.pk, book.title)
        return redirect('library:book_list')

    return render(request, 'library/book_form.html', {'action': 'Add'})


def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        old_title = book.title

        book.title = request.POST.get('title', '').strip()
        book.author = request.POST.get('author', '').strip()
        book.isbn = request.POST.get('isbn', '').strip()
        book.published_year = int(request.POST.get('published_year', 0))
        book.save()

        logger.info("Book updated. ID: %s, Old Title: %s, New Title: %s",
                    book.pk, old_title, book.title)

        return redirect('library:book_list')

    return render(request, 'library/book_form.html',
                  {'data': {'title': book.title, 'author': book.author,
                            'isbn': book.isbn, 'published_year': book.published_year},
                   'action': 'Edit'})


def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        book.delete()  # soft delete
        logger.warning("Book soft-deleted. ID: %s, Title: %s", book.pk, book.title)
        return redirect('library:book_list')

    return render(request, 'library/book_confirm_delete.html', {'book': book})


def trash_list(request):
    cutoff = timezone.now() - timedelta(days=1)
    deleted = Book.all_objects.filter(is_deleted=True, deleted_at__gte=cutoff)

    logger.info("Trash list accessed. Items found: %s", deleted.count())

    return render(request, 'library/trash_list.html', {'books': deleted})


def book_restore(request, pk):
    book = get_object_or_404(Book.all_objects, pk=pk, is_deleted=True)

    if book.is_recoverable:
        book.restore()
        logger.info("Book restored. ID: %s, Title: %s", book.pk, book.title)
    else:
        logger.warning("Attempt to restore non-recoverable book. ID: %s", book.pk)

    return redirect('library:trash_list')


def book_hard_delete(request, pk):
    book = get_object_or_404(Book.all_objects, pk=pk)

    if request.method == 'POST':
        logger.error("Book permanently deleted. ID: %s, Title: %s", book.pk, book.title)
        book.delete(hard=True)
        return redirect('library:trash_list')

    return render(request, 'library/book_confirm_hard_delete.html', {'book': book})