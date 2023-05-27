from itertools import groupby
from typing import Any, List

from fastapi import APIRouter
from fastapi import status as status_code
from jsql import sql
from Models import (
    InvoiceGroup,
    InvoiceItem,
    InvoiceGroupSubscription,
    RecurringType,
    ServerMessage,
    VarlaResponse,
    VarlaResponseBody,
)
from Utility.context import g

retrieve = APIRouter(prefix="/invoices", tags=["Invoice Group"])


def group_by(
    items: List[Any],
    key: str,
    *,
    group_key: str = "items",
    key_value_transformation: callable = lambda x: x,
    sort: bool = False,
):
    if sort:
        items.sort(key=(lambda x: x[key]))

    return [
        {key: key_value_transformation(k), group_key: list(v)}
        for k, v in groupby(items, key=lambda x: x[key])
    ]


@retrieve.post("/get/groups", response_model=VarlaResponse[List[InvoiceGroup.Object]])
def get_invoice_groups(filter: InvoiceGroup.Filter):
    try:
        invoice_groups: List[InvoiceGroup.Object] = sql(
            g().conn,
            """
                SELECT
                    IG.*,
                    COALESCE(II.total_paid,0) AS "total_paid", 
                    IGS.next_on,
                    IGS.group_currency AS "currency",
                    COALESCE(IGS.daily_deduction_amount,0) AS "daily_deduction_amount",
                    COALESCE(IGS.weekly_deduction_amount,0) AS "weekly_deduction_amount",
                    COALESCE(IGS.monthly_deduction_amount,0) AS "monthly_deduction_amount",
                    COALESCE(IGS.yearly_deduction_amount,0) AS "yearly_deduction_amount"
                FROM
                    invoice_group AS IG
                    LEFT JOIN(
                        SELECT
                            group_id,
                            SUM(amount) AS total_paid
                        FROM
                            invoice_item
                        WHERE confirmed

                        GROUP BY
                            group_id
                    ) AS II ON IG.id = II.group_id
                    LEFT JOIN(
                        SELECT
                            group_id,
                            min(currency) AS group_currency,
                            MIN(
                                DATE_ADD(
                                    CURDATE(),
                                    INTERVAL DATEDIFF(
                                        (
                                            CASE
                                                WHEN recurring_type = 3 THEN IF(
                                                    DATE_FORMAT(
                                                        deduction_date,
                                                        CONCAT(
                                                            YEAR(CURDATE()),
                                                            "-",
                                                            MONTH(CURDATE()),
                                                            "-%d"
                                                        )
                                                    ) < CURDATE(),
                                                    DATE_ADD(
                                                        DATE_FORMAT(
                                                            deduction_date,
                                                            CONCAT(
                                                                YEAR(CURDATE()),
                                                                "-",
                                                                MONTH(CURDATE()),
                                                                "-%d"
                                                            )
                                                        ),
                                                        INTERVAL 1 MONTH
                                                    ),
                                                    DATE_FORMAT(
                                                        deduction_date,
                                                        CONCAT(
                                                            YEAR(CURDATE()),
                                                            "-",
                                                            MONTH(CURDATE()),
                                                            "-%d"
                                                        )
                                                    )
                                                )
                                                WHEN recurring_type = 4 THEN IF(
                                                    DATE_FORMAT(
                                                        deduction_date,
                                                        CONCAT(
                                                            YEAR(CURDATE()),
                                                            "-%m-%d"
                                                        )
                                                    ) < CURDATE(),
                                                    DATE_ADD(
                                                        DATE_FORMAT(
                                                            deduction_date,
                                                            CONCAT(
                                                                YEAR(CURDATE()),
                                                                "-%m-%d"
                                                            )
                                                        ),
                                                        INTERVAL 1 YEAR
                                                    ),
                                                    DATE_FORMAT(
                                                        deduction_date,
                                                        CONCAT(
                                                            YEAR(CURDATE()),
                                                            "-%m-%d"
                                                        )
                                                    )
                                                )
                                                ELSE "9999-12-31"
                                            END
                                        ),
                                        CURDATE()
                                    ) DAY
                                )
                            ) AS "next_on",
                            SUM(
                                IF(recurring_type = 1, amount, 0)
                            ) AS "daily_deduction_amount",
                            SUM(
                                IF(recurring_type = 2, amount, 0)
                            ) AS "weekly_deduction_amount",
                            SUM(
                                IF(recurring_type = 3, amount, 0)
                            ) AS "monthly_deduction_amount",
                            SUM(
                                IF(recurring_type = 4, amount, 0)
                            ) AS "yearly_deduction_amount"
                        FROM
                            invoice_group_subscription
                        WHERE
                            NOT is_stopped
                        GROUP BY
                            group_id
                    ) AS IGS ON IG.id = IGS.group_id
                WHERE TRUE
                {% if id %}                     AND id = :id                             {% endif %}
                {% if start_date %}             AND start_date = :start_date             {% endif %}
                {% if name %}                   AND name LIKE "%{{name}}%"               {% endif %}
            """,
            **filter.dict(),
        ).dicts()

        return VarlaResponse[List[InvoiceGroup.Object]](
            body=VarlaResponseBody(data=invoice_groups, type="List[InvoiceGroup]"),
            server_message=ServerMessage(
                status_code=status_code.HTTP_200_OK, message="Ok"
            ),
            varla_message="Here!",
        )
    except Exception as e:
        print(e)
        return VarlaResponse(
            server_message=ServerMessage(
                status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e),
            ),
            varla_message="oops!",
        )


@retrieve.post(
    "/get/subscriptions",
    response_model=VarlaResponse[List[InvoiceGroupSubscription.Object]],
)
def get_invoice_group_subscriptions(filter: InvoiceGroupSubscription.Filter):
    print(filter)
    try:
        subscriptions: List[InvoiceGroupSubscription.Object] = sql(
            g().conn,
            """
                SELECT
                    id,
                    group_id,
                    name,
                    amount,
                    currency,
                    description,
                    recurring_type,
                    is_stopped,
                    TIMESTAMP(
                        CASE
                            WHEN recurring_type = 3 THEN IF(
                                DATE_FORMAT(
                                    deduction_date,
                                    CONCAT(
                                        YEAR(CURDATE()),
                                        "-",
                                        MONTH(CURDATE()),
                                        "-%d"
                                    )
                                ) < CURDATE(),
                                DATE_ADD(
                                    DATE_FORMAT(
                                        deduction_date,
                                        CONCAT(
                                            YEAR(CURDATE()),
                                            "-",
                                            MONTH(CURDATE()),
                                            "-%d"
                                        )
                                    ),
                                    INTERVAL 1 MONTH
                                ),
                                DATE_FORMAT(
                                    deduction_date,
                                    CONCAT(
                                        YEAR(CURDATE()),
                                        "-",
                                        MONTH(CURDATE()),
                                        "-%d"
                                    )
                                )
                            )
                            WHEN recurring_type = 4 THEN IF(
                                DATE_FORMAT(
                                    deduction_date,
                                    CONCAT(
                                        YEAR(CURDATE()),
                                        "-%m-%d"
                                    )
                                ) < CURDATE(),
                                DATE_ADD(
                                    DATE_FORMAT(
                                        deduction_date,
                                        CONCAT(
                                            YEAR(CURDATE()),
                                            "-%m-%d"
                                        )
                                    ),
                                    INTERVAL 1 YEAR
                                ),
                                DATE_FORMAT(
                                    deduction_date,
                                    CONCAT(
                                        YEAR(CURDATE()),
                                        "-%m-%d"
                                    )
                                )
                            )
                            ELSE "9999-12-31"
                        END
                    ) AS deduction_date
                FROM
                    invoice_group_subscription
        

                WHERE True
                    {% if id %}                         AND id = :id                             {% endif %}
                    {% if group_id %}                   AND group_id = :group_id                 {% endif %}
                    {% if currency %}                   AND currency = :currency                 {% endif %}
                    {% if name %}                       AND name LIKE "%{{name}}%"               {% endif %}
                    {% if description %}                AND description LIKE "%{{description}}%" {% endif %}
                    {% if recurring_type != -1 %}       AND recurring_type = :recurring_type     {% endif %}
                    {% if is_stopped != None %}         AND is_stopped=:is_stopped               {% endif %} 

                ORDER BY
                    group_id,
                    deduction_date
            """,
            **filter.dict(),
        ).dicts()

        # subscriptions: List[InvoiceGroupSubscription.Object] = group_by(
        #     subscriptions,
        #     "group_id",
        #     group_key="subscriptions",
        #     key_value_transformation=lambda x: int(x),
        # )

        return VarlaResponse[List[InvoiceGroupSubscription.Object]](
            body=VarlaResponseBody(
                data=subscriptions,
                type="List[InvoiceGroupSubscription.Object]",
            ),
            server_message=ServerMessage(
                status_code=status_code.HTTP_200_OK, message="Ok"
            ),
            varla_message="Here!",
        )
    except Exception as e:
        print(e)
        return VarlaResponse(
            server_message=ServerMessage(
                status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e),
            ),
            varla_message="oops!",
        )


@retrieve.post("/get/invoices", response_model=VarlaResponse[List[InvoiceItem.Object]])
def get_invoice_items(filter: InvoiceItem.Filter):
    try:
        print(filter)
        invoice_items: List[InvoiceItem.Object] = sql(
            g().conn,
            """
                SELECT
                    II.*,
                    TIMESTAMP(II.deduction_date) AS "deduction_date"
                FROM
                    `invoice_item` AS II
                LEFT JOIN `invoice_group` AS IG
                ON
                    group_id = IG.id 

                WHERE True
                    {% if id %}                         AND id = :id                             {% endif %}
                    {% if group_id %}                   AND group_id = :group_id                 {% endif %}
                    {% if currency %}                   AND currency = :currency                 {% endif %}
                    {% if deduction_type != -1 %}       AND deduction_type = :deduction_type     {% endif %}
                    {% if description %}                AND description LIKE "%{{description}}%" {% endif %}
                    {% if confirmed != None %}          AND confirmed=:confirmed                 {% endif %}  

            """,
            **filter.dict(),
        ).dicts()

        print(invoice_items)
        return VarlaResponse[List[InvoiceItem.Object]](
            body=VarlaResponseBody(data=invoice_items, type="List[InvoiceItem]"),
            server_message=ServerMessage(
                status_code=status_code.HTTP_200_OK, message="Ok"
            ),
            varla_message="Here!",
        )
    except Exception as e:
        print(e)
        return VarlaResponse(
            server_message=ServerMessage(
                status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e),
            ),
            varla_message="oops!",
        )
